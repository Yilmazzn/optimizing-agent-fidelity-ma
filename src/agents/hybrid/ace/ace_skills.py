import os
import uuid
import json
import asyncio
from loguru import logger
import numpy as np
from typing import List, Dict, Optional, Literal, Any
import openai
from pydantic import BaseModel, Field, PrivateAttr
from openai import AsyncOpenAI

from utils import get_openai_client

# https://arxiv.org/pdf/2510.04618

# --- 1. Data Models (Pydantic) ---

class Skill(BaseModel):
    """
    Represents a single context item (bullet) in the ACE framework.
    See Section 3.1: "context as a collection of structured, itemized bullets...
    consisting of metadata... and content." 
    """
    content: str
    section: str
    skill_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    
    # Metadata for tracking efficacy [cite: 183]
    helpful_count: int = 0
    harmful_count: int = 0
    
    # Cached embedding for deduplication (excluded from serialization)
    _embedding: Optional[List[float]] = PrivateAttr(default=None)

    def to_context_string(self) -> str:
        """Formats the skill for the LLM context (e.g., [id] content)."""
        return f"[{self.skill_id}] {self.content}"

class ReflectorTag(BaseModel):
    """Represents the tagging of a specific bullet point."""
    id: str
    tag: Literal['helpful', 'harmful', 'neutral']

class ReflectorOutput(BaseModel):
    """
    Structured output from the Reflector.
    Based on Appendix D, Figure 13. [cite: 817-828]
    """
    reasoning: str
    error_identification: Optional[str] = None
    root_cause_analysis: Optional[str] = None
    correct_approach: Optional[str] = None
    key_insight: Optional[str] = None
    bullet_tags: List[ReflectorTag] = Field(default_factory=list)

class CuratorOperation(BaseModel):
    """
    Represents an atomic update to the playbook.
    Based on Appendix D, Figure 14. [cite: 858-860]
    """
    type: Literal['ADD']  # ACE primarily uses incremental adds [cite: 189]
    section: str
    content: str

class CuratorOutput(BaseModel):
    """
    Structured output from the Curator.
    Based on Appendix D, Figure 14. [cite: 851-855]
    """
    reasoning: str
    operations: List[CuratorOperation] = Field(default_factory=list)


# --- 2. ACE Playbook (Skill Management) ---

class ACEPlaybook(BaseModel):
    """
    The 'Evolving Playbook' that accumulates and organizes strategies.
    Implements 'Grow-and-Refine' strategy[cite: 192].
    """
    skills: Dict[str, Skill] = Field(default_factory=dict)

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.client = openai.OpenAI(
            base_url=os.getenv("AZURE_OPENAI_BASE_URL"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        )

    def add_skill(self, content: str, section: str) -> str:
        new_skill = Skill(content=content, section=section)
        self.skills[new_skill.skill_id] = new_skill
        return new_skill.skill_id

    def update_stats(self, skill_id: str, tag: str):
        if skill_id in self.skills:
            if tag == 'helpful':
                self.skills[skill_id].helpful_count += 1
            elif tag == 'harmful':
                self.skills[skill_id].harmful_count += 1

    def get_context(self) -> str:
        """
        Compiles the playbook into a text string for the Generator.
        Groups skills by section for readability.
        """
        if not self.skills:
            return ""

        sections: Dict[str, List[Skill]] = {}
        for skill in self.skills.values():
            sections.setdefault(skill.section, []).append(skill)

        context_lines = ["ACE PLAYBOOK:"]
        for section, skills in sections.items():
            context_lines.append(f"\n=== {section.upper()} ===")
            for skill in skills:
                context_lines.append(skill.to_context_string())
        
        return "\n".join(context_lines)

    def deduplicate(self, client: AsyncOpenAI, threshold: float = 0.85):
        """
        Implements the 'Refine' step of Grow-and-Refine.
        Prunes redundancy by comparing bullets via semantic embeddings[cite: 195].
        """
        ids = list(self.skills.keys())
        if len(ids) < 2:
            return

        # 1. Fetch/Cache Embeddings
        for skill_id in ids:
            skill = self.skills[skill_id]
            if skill._embedding is None:
                skill._embedding = self._fetch_embedding(client, skill.content)

        # 2. Compare and Prune (Naive O(N^2) for demonstration)
        to_remove = set()
        for i in range(len(ids)):
            if ids[i] in to_remove:
                continue
            
            vec_a = self.skills[ids[i]]._embedding
            
            for j in range(i + 1, len(ids)):
                if ids[j] in to_remove:
                    continue

                vec_b = self.skills[ids[j]]._embedding
                similarity = self._cosine_similarity(vec_a, vec_b)

                if similarity > threshold:
                    # Resolve conflict: Keep the one with higher helpfulness [cite: 183]
                    # If equal, keep the older one (arbitrary tie-break)
                    skill_a = self.skills[ids[i]]
                    skill_b = self.skills[ids[j]]
                    
                    score_a = skill_a.helpful_count - skill_a.harmful_count
                    score_b = skill_b.helpful_count - skill_b.harmful_count

                    if score_b > score_a:
                        to_remove.add(ids[i])
                        break # skill_a is removed, stop comparing it
                    else:
                        to_remove.add(ids[j])

        # 3. Execute Removal
        for uid in to_remove:
            del self.skills[uid]
        
        logger.info(f"Deduplication complete. Removed {len(to_remove)} redundant skills.")

    def _fetch_embedding(self, text: str) -> List[float]:
        response = self.client.embeddings.create(input=text, model="text-embedding-3-small")
        return response.data[0].embedding
        
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        vec_a = np.array(a)
        vec_b = np.array(b)
        return np.dot(vec_a, vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b))



class ACEManager:
    """
    Orchestrates the agentic workflow: Generator -> Reflector -> Curator.
    See Figure 4 in the paper[cite: 175].
    """
    def __init__(self):
        self.client = get_openai_client()
        self.playbook = ACEPlaybook()

    def learn(self, task_query: str, previous_response_id: str):

        # --- Step 2: REFLECTOR [cite: 158] ---
        # "Distills concrete insights, failure loops, and key learnings"
        reflection = self._reflector_step(task_query)

        # Apply Reflector Feedback (Tagging)
        for tag_data in reflection.bullet_tags:
            self.playbook.update_stats(tag_data.id, tag_data.tag)

        # --- Step 3: CURATOR [cite: 159] ---
        # "Integrates insights into structured context updates (Deltas)"
        curation = self._curator_step(task_query, trajectory, reflection, current_context)

        # Apply Curator Operations (Incremental Updates) [cite: 189]
        for op in curation.operations:
            if op.type == 'ADD':
                new_id = self.playbook.add_skill(op.content, op.section)
                print(f"Added new skill [{new_id}] to section '{op.section}'")

        self.playbook.deduplicate(self.client, threshold=0.85)


    def _reflector_step(self, query: str, trajectory: str, answer: str, ground_truth: str, context: str) -> ReflectorOutput:
        """
        Simulates the Reflector role.
        Prompt structure references Appendix D, Figure 13[cite: 830].
        """
        # prompt = ... (See Figure 13 for exact text)
        
        # Simulating structured JSON return from LLM
        mock_response_json = {
            "reasoning": "The model failed to check boundary conditions.",
            "error_identification": "Off-by-one error",
            "root_cause_analysis": "The loop range was inclusive/exclusive mismatch.",
            "correct_approach": "Use range(n+1)",
            "key_insight": "Always verify loop boundaries.",
            "bullet_tags": [] 
        }
        return ReflectorOutput(**mock_response_json)

    def _curator_step(self, query: str, trajectory: str, reflection: ReflectorOutput, context: str) -> CuratorOutput:
        """
        Simulates the Curator role.
        Prompt structure references Appendix D, Figure 14[cite: 861].
        """
        # prompt = ... (See Figure 14 for exact text)
        
        # Simulating structured JSON return from LLM
        mock_response_json = {
            "reasoning": "The error suggests we need a specific rule for loops.",
            "operations": [
                {
                    "type": "ADD",
                    "section": "CODING_BEST_PRACTICES",
                    "content": "When iterating with ranges, double check inclusive vs exclusive bounds."
                }
            ]
        }
        return CuratorOutput(**mock_response_json)

# --- Usage Example ---

def main():
    ace = ACEManager(api_key="sk-placeholder")
    
    # 1. First Run (Empty Playbook)
    ace.run_episode(
        task_query="Calculate the sum of integers from 1 to 10.",
        ground_truth="55"
    )
    
    # 2. Second Run (Playbook has new skill)
    ace.run_episode(
        task_query="Calculate the sum of integers from 1 to 100.",
        ground_truth="5050"
    )

if __name__ == "__main__":
    asyncio.run(main())