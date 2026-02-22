import json
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential
from agents.hybrid.skill_agent_2.reflector import Learning, SkillNegative, SkillNeutral, SkillNotFollowed, SkillPositive, SkillReview
from agents.hybrid.skill_agent_2.skill_book import Skill, SkillBook
from agents.hybrid.skill_agent_2.skill_manager_tools import SkillManagerTools
from domain.request import TokenUsage
from utils import get_openai_client, get_tool_calls_from_response

_SYSTEM_PROMPT_LEARNER = """
## Skillbook Manager

You are an expert senior skill book manager that helps maintain and improve a skillbook used by AI agents to operate computer systems.

Maintain a skillbook of **non-obvious knowledge** for computer use agents—menu locations, shortcuts, prerequisites, correct procedures. Not basic computer literacy.

You operate in a multi-turn tool-calling fashion to interact with the skill book to ingest/reject new learnings. Finish by not calling a tool anymore, but by responding with a summary of your actions.

### Inputs

You receive one item at a time:

**Learning** — New guidance discovered from a trajectory
- `scope`: Application (e.g., "gimp") or "general"/"os"
- `situation`, `guidance`, `confidence` (low/medium/high)
- *Intent:* Integrate valuable knowledge into the skillbook—explore for similar skills first, then create, update, or merge as appropriate.

**SkillReview** — Feedback on a skill after it was used (or retrieved but not used):

- **SkillNegative** — Skill was followed but caused friction or errors
  - `followed`, `issue_type` (incorrect/incomplete/unclear), `what_went_wrong`, `corrected_guidance`
  - *Intent:* Fix or annotate. If corrected guidance is provided and confident, update. Otherwise annotate for future review.
  - If multiple negative reviews of same type, but no corrected guidance, consider deletion

- **SkillNeutral** — Skill was followed but had no meaningful effect
  - `followed`, `reason` (not_needed/marginal), `suggested_improvement`
  - *Intent:* Evaluate relevance. Consider if the skill's scope is too broad or if it should be refined.

- **SkillNotFollowed** — Skill was retrieved but not trusted/used
  - `reason` (irrelevant/chose_alternative/seemed_wrong), `explanation`
  - *Intent:* Investigate. If "seemed_wrong"—the skill may need correction. If "irrelevant"—consider if the skill's description is misleading.

**General Cleanup Instruction** — When 'Cleanup!' is called

### Tools

**Reading:**
- `fetch_similar_skills(domain, skill_description)` — Find related skills
- `read_skills(skill_ids)` — Get content, annotations, metrics 

**Writing:**
- `create_domain(domain, description)`
- `create_skill(domain, skill_name, description, body)`
- `update_skill(skill_id, description?, body?, dismiss_annotations?)`
- `merge_skills(source_skill_id, target_skill_id, description, body)`
- `annotate_skill(skill_id, annotation)`
- `delete_skill(skill_id)`

### Writing Effective Skills

Skills have two key components:

**Description** (10-100 chars): The triggering mechanism. Used for semantic search to find relevant skills.
- Must clearly capture WHEN to use this skill
- Include key terms the agent would search for
- Example: "Making colors or backgrounds transparent in images"

**Body** (20-3000 chars): The actual instructions in markdown. Loaded only when the skill is retrieved.

#### Body Writing Principles

**1. Conciseness is key** — The agent's context window is shared with the task, conversation, and other skills. Only include what the agent doesn't already know. Challenge each line: "Does this justify its token cost?"

**2. Match specificity to fragility:**
- *High freedom* (general guidance): When multiple approaches work, use heuristics
- *Medium freedom* (patterns with options): When a preferred approach exists but variation is acceptable  
- *Low freedom* (exact steps): When operations are fragile, error-prone, or sequence-critical

**3. Structure for multiple cases** — A skill can cover multiple related scenarios. Use clear sections:
```markdown
## Case 1: [Scenario]
[Steps or guidance]

## Case 2: [Scenario]  
[Steps or guidance]
```

**4. Be concrete and sequential** — For procedures, use numbered steps with exact menu paths, shortcuts, and UI elements. Prefer examples over explanations.

**5. Non-obvious knowledge only** — Don't explain basic concepts. Focus on:
- Hidden menu locations
- Required prerequisites or setup
- Steps requiring complex knowledge or logic
- Common pitfalls and how to avoid them
- Keyboard shortcuts for efficiency
- Correct sequences when order matters

#### Example Skill Body

```markdown
## Adding Transparency
1. Select the target layer in the Layers panel
2. Go to Layer > Transparency > Add Alpha Channel (skip if "Add Alpha Channel" is grayed out)
3. Use the Fuzzy Select tool (U) to select the area
4. Press Delete to make it transparent

## Removing Color (Color to Alpha)
1. Select the layer
2. Go to Colors > Color to Alpha
3. Pick the color to remove
4. Adjust threshold for partial transparency

Note: Both methods require an alpha channel. Check Layer > Transparency first.
```

### Process

1. **Explore** — Check for similar skills first
2. **Decide** — What action (if any)?
3. **Act** — Call tools to interact with the skill book or finish

#### Cleanup!

When you receive a 'Cleanup!' instruction, you will also optionally receive similar skill pairs. Perform these steps:
- Identify whether skills are similar based on their descriptions
- Read out the ones that seem similar via `read_skills` and could contain similar skill guidance.
- If they are indeed similar (overlap in content), merge them using `merge_skills` with a more general description and combined body.
- If title/description misalign with new skill, create a new skill that generalizes both with `create_skill`, and delete the originals.

Repeat if relevant.

**Outside of the similar pairs provided, you can proactively search for other similar skills given the previous list**

**If none are really similar, simply respond with 'No reasonable merge.'**

### Principles

- **Explore before creating** — Avoid duplicates
- **MECE** — The most important property of the skill book. Skills should be Mutually Exclusive and Collectively Exhaustive in scope. Consider merging, updating, or deleting skills to maintain MECE.
- **Right granularity** — Skills should be cohesive, not fragmented. Consolidate related operations into a single skill rather than many micro-skills.
  - ✓ Good: `chrome/settings`, `gimp/transparency`, `libreoffice-calc/formulas`, `chrome/bookmarks`
  - ✗ Bad: `chrome/open-settings`, `chrome/change-homepage`, `chrome/clear-cache` (too fragmented—merge into `chrome/settings`)
  - ✗ Bad: `gimp/add-transparency`, `gimp/remove-transparency` (merge into `gimp/transparency`)
- **Confidence matters** — Low confidence → annotate or skip. Medium/high → act.
- **Annotations are history:**
  - Multiple similar complaints → pattern confirmed, safe to update
  - Conflicting annotations → be conservative, annotate
  - Single report, no prior annotations → annotate, don't update yet (if not high confidence wrong)
- **Dismiss annotations** when your update directly fixes the issues they describe
- **Concrete and sequential** — Write numbered steps with exact menu paths, shortcuts, UI elements
- **Generalizable only** — No task-specific details, no basic knowledge (e.g. 'chrome/manage-bookmarks', instead of more detailing single operations)
- **Conservative when uncertain** — Annotate rather than update or delete
- **Preserve knowledge** — Update/merge over delete, unless truly redundant, obsolete, or multiple negative reviews/impacts
- **Metrics guide action** — High usage/positive impact → be cautious updating. Low usage/negative impact → more willing to change.
- **Reasonable skill book size** — Avoid bloat. Avoid extreme minimalism. (Too many skills → hard to find/use. Too few → lacks needed guidance.)

### Available Skills
{skills_list}

""".strip()

class SkillManager:
    def __init__(self, skill_book: SkillBook):
        self.skill_book = skill_book
        self.tools = SkillManagerTools(skill_book=skill_book)
        self.client = get_openai_client()
    
    @retry(
       reraise=True,
       stop=stop_after_attempt(4),
       wait=wait_exponential(multiplier=1.0, min=1.0, max=8.0),
    )
    def _make_call(self, prompt: str, tool_results: list, previous_response_id: str = None):
        _input = tool_results
        _input.append({
            "role": "user",
            "content": [{
                "type": "input_text",
                "text": prompt
            }]
        })
        response = self.client.responses.create(
            model="gpt-5.2",
            reasoning={"effort": "high"},
            input=_input,
            instructions=self.system_prompt,
            previous_response_id=previous_response_id,
            tools=self.tools.get_tools(),
            tool_choice="auto",
        )
        self.last_response_id = response.id
        return response
    
    def call_llm(self, obj: BaseModel, input_type: str, override_prompt: str = None) -> tuple[list[dict], TokenUsage]:
        token_usage = TokenUsage()
        tool_results = []
        history = []
        previous_response_id = None
        if override_prompt:
            prompt = override_prompt
        else:
            prompt = f"Process '{input_type}'" + "\n\n" + json.dumps(obj.model_dump_json(indent=4))

        while True:
            response = self._make_call(
                prompt=prompt, 
                tool_results=tool_results, 
                previous_response_id=previous_response_id
            )
            prompt = "continue or finish"
            previous_response_id = response.id
            token_usage += TokenUsage.from_response(response)
            tool_calls = get_tool_calls_from_response(response)

            tool_results = []
            for tool_call in tool_calls:
                tool_result = self.tools.parse_action(tool_call)
                tool_results.append(tool_result)
                history.append({
                    "tool_call": {
                        "name": tool_call.name,
                        "arguments": json.loads(tool_call.arguments)
                    },
                    "tool_result": tool_result
                })
            if len(tool_calls) == 0:
                break

        history.append({
            "final_response": response.output_text
        })
        return history, token_usage
    
    def _format_skills(self) -> str:
        skill_list = ""
        for domain in self.skill_book.get_domain_ids():
            skill_list += f"## Domain: `{domain}`\n"
            skill_domain = self.skill_book.get_domain(domain)
            skills = skill_domain.get_skills()
            for skill in skills:
                skill_list += f"- `{skill.id}`: {skill.description} (Used {skill.metrics.times_requested} times, Positive Impact: {skill.metrics.positive_impact}, Negative Impact: {skill.metrics.negative_impact})\n"
        return skill_list
    
    def learn(self, reviews: list[SkillReview], learnings: list[Learning]) -> list[dict]:
        self.system_prompt = _SYSTEM_PROMPT_LEARNER.format(
            skills_list=self._format_skills()
        )
        reviews_to_process = [self.manage_skill_review(r) for r in reviews]
        reviews_to_process = list(filter(lambda r: r is not None, reviews_to_process))

        learning_history = []
        for review in reviews_to_process:
            hist, token_usage = self.call_llm(review, "SkillReview")
            learning_history.append({
                "review": review.model_dump(),
                "skill_manager": hist,
                "token_usage": token_usage.model_dump()
            })

        for learning in learnings:
            hist, token_usage = self.call_llm(learning, "Learning")
            learning_history.append({
                "learning": learning.model_dump(),
                "skill_manager": hist,
                "token_usage": token_usage.model_dump()
            })
        return learning_history
    
    def manage_skill_review(self, review: SkillReview):
        skill = self.skill_book.get_skill(review.skill_id)
        skill.metrics.times_requested += 1

        if isinstance(review, SkillPositive):
            skill.metrics.positive_impact += 1
            skill.metrics.times_followed += 1

        elif isinstance(review, SkillNeutral):
            skill.metrics.neutral_impact += 1
            skill.metrics.times_followed += 1 if review.followed == "yes" else 0.5
            if review.suggested_improvement is not None:
                return review

        elif isinstance(review, SkillNegative):
            skill.metrics.negative_impact += 1
            skill.metrics.times_followed += 1 if review.followed == "yes" else 0.5
            return review
        
        elif isinstance(review, SkillNotFollowed):
            if review.reason == "seemed_wrong":
                return review
            if review.reason == "chose_alternative":
                skill.annotate(f"Skill not followed [{review.reason}]: {review.explanation}")

    def cleanup(self) -> dict:
        similar_skill_pairs = []
        for domain in self.skill_book.get_domain_ids():
            domain_similar_skill_pairs = self.skill_book.find_similar_skill_pairs(domain=domain, threshold=0.5)
            similar_skill_pairs.extend(domain_similar_skill_pairs)
            
        prompt = "Cleanup!"
        if len(similar_skill_pairs) > 0:
            prompt += "\n\nSimilar skill pairs:\n"
            for pair in similar_skill_pairs:
                prompt += f"- `{pair[0].id}` and `{pair[1].id}` (similarity: {pair[2]:.2f})\n"

        cleanup_history, token_usage = self.call_llm(obj={}, input_type="Cleanup!", override_prompt=prompt)
        return {
            "cleanup_history": cleanup_history,
            "token_usage": token_usage.model_dump()
        }