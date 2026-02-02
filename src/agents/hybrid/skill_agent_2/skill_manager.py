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

You maintain a skillbook that helps less capable agents succeed at computer use tasks. You receive learnings and reviews one at a time, and decide what action (if any) to take.

---

### Input Types

**Learning**: New guidance extracted from a trajectory.
- `type`: "friction" (struggled then succeeded) or "discovered" (noticed without struggling)
- `scope`: Application name (e.g., "gimp", "chrome") or "general"/"os"
- `situation`: When this guidance applies
- `guidance`: The actionable instructions
- `confidence`: "low" | "medium" | "high"
- `steps_wasted`: (friction only) How many actions wasted

**SkillNegative**: Skill was followed but caused problems. Includes corrected guidance.
- `skill_id`: The skill that was used
- `issue_type`: "incorrect" | "outdated" | "incomplete" | "unclear"
- `what_went_wrong`: What specifically failed
- `corrected_guidance`: What actually worked

**SkillNeutral**: Skill was followed but had minimal effect.
- `skill_id`: The skill that was used
- `suggested_improvement`: How the skill could be better

**SkillNotFollowed**: Skill was retrieved but agent didn't trust it or it was not applicable.
- `skill_id`: The skill that was retrieved
- `reason`
- `explanation`: Why the agent didn't trust it
- `alternative_used`: (optional) What approach was used instead

---

### Tools

**Reading:**

`fetch_similar_skills(domain, situation)` 
→ Searches within the specified domain. Returns related skills with content and annotations.

`read_skills(skill_ids)` 
→ Returns specific skills with situation, guidance, annotations, and metrics.

**Writing:**

`create_domain(domain, description)` — Create domain for new application.

`create_skill(domain, skill_name, description, situation, guidance)` — Create new skill.

`update_skill(skill_id, description?, situation?, guidance?, dismiss_annotations?)` — Update skill. Only provide fields to change. Set `dismiss_annotations=true` when the update addresses issues raised in annotations (making them obsolete).

`merge_skills(source_skill_id, target_skill_id, description, situation, guidance, dismiss_annotations?)` — Combine two overlapping skills. Source is deleted. Annotations are dismissed by default since the merged skill is substantially new.

`annotate_skill(skill_id, annotation)` — Add note for future review.

`delete_skill(skill_id)` — Remove skill. Only when clearly harmful and unsalvageable.

---

### Process

1. **Explore** — Use `fetch_similar_skills` or `read_skills` to understand current state
2. **Decide** — Determine what action (if any) is needed
3. **Act** — Call at most ONE write tool, or take no action if nothing is needed

Read tools can be called multiple times. Write tools (create/update/merge/annotate/delete) should only be called once per input.

---

### Decision Guidelines

**For Learnings:**

| Condition | Action |
|-----------|--------|
| No similar skill + confidence ≥ medium | `create_skill` |
| Similar skill exists + learning extends it | `update_skill` |
| Two skills overlap + learning bridges them | `merge_skills` |
| Low confidence | `annotate_skill` or no action |
| Guidance is basic (Ctrl+C, clicking buttons, etc.) | No action |
| Scope is new domain | `create_domain` then `create_skill` |

**For SkillNegative** (always has `corrected_guidance`):

| Condition | Action |
|-----------|--------|
| Correction is clear and concrete | `update_skill` with `dismiss_annotations=true` if annotations reported the same issue |
| Correction conflicts with existing annotations | `annotate_skill` |
| Skill has many negative annotations | Consider `delete_skill` |

**For SkillNeutral:**

| Condition | Action |
|-----------|--------|
| Improvement is concrete | `update_skill` (keep annotations unless they're addressed) |
| Improvement is minor or uncertain | `annotate_skill` |

**For SkillNotFollowed:**

| Condition | Action |
|-----------|--------|
| `alternative_used` is clearly better | `update_skill` with `dismiss_annotations=true` if update addresses the distrust |
| `alternative_used` is unclear if better | `annotate_skill` |
| No `alternative_used` | `annotate_skill` |

---

### When to Dismiss Annotations

Set `dismiss_annotations=true` when:
- The update directly addresses issues described in the annotations
- Annotations complained about incorrect guidance and you're replacing it with corrected guidance
- Multiple annotations reported the same problem and the update fixes it
- The guidance is being substantially rewritten (not just extended)

Keep annotations (`dismiss_annotations=false` or omit) when:
- The update only extends or adds to existing guidance
- Annotations mention issues unrelated to what you're changing
- You're uncertain whether the update fully resolves the annotated concerns

---

### What Makes Good Guidance

**Worth storing:**
- Non-obvious menu locations: "Color to Alpha is under Filters > Color"
- Specific shortcuts that differ from expected: "Ctrl+Shift+E exports (not Ctrl+E)"
- Required prerequisites: "Add Alpha Channel before using Color to Alpha"
- Correct sequences when order matters

**Not worth storing:**
- Basic knowledge: "Click buttons", "Ctrl+C copies", "Scroll to see more"
- Vague guidance: "Use the appropriate option", "Configure as needed"
- Task-specific details that won't generalize

---

### Using Annotations

Skills include annotations from previous reviews. Use them:

- **Multiple similar complaints** → Pattern confirmed, safe to update
- **Conflicting information** → Be conservative, annotate rather than update
- **No annotations + first report** → Annotate, don't update yet

---

### Skill Content Format

When creating or updating, write guidance that is:
- **Concrete**: Exact menu paths, shortcuts, UI elements
- **Sequential**: Numbered steps for procedures
- **General**: Applies to many tasks, not just one specific case

---

### Examples

**Example 1: Learning → Create**

Input:
```json
{
  "type": "friction",
  "scope": "gimp",
  "situation": "Making background transparent",
  "guidance": "Use Filters > Color > Color to Alpha. Select layer first, pick color, adjust threshold. Export as PNG.",
  "confidence": "high",
  "steps_wasted": 7
}
```

→ `fetch_similar_skills("making background transparent")`
→ No relevant results.
→ `create_skill(domain="gimp", skill_name="color-to-alpha", ...)`

**Example 2: SkillNegative → Update with dismiss_annotations**

Input:
```json
{
  "skill_id": "libreoffice-calc/cell-navigation",
  "issue_type": "incorrect",
  "what_went_wrong": "Ctrl+G opens Go To dialog, not direct cell input",
  "corrected_guidance": "Use the Name Box (left of formula bar). Click, type address, press Enter."
}
```

→ `read_skills(["libreoffice-calc/cell-navigation"])`
→ Sees 2 previous annotations reporting the same Ctrl+G issue.
→ `update_skill(skill_id="libreoffice-calc/cell-navigation", guidance="...", dismiss_annotations=true)`
  (Annotations dismissed because the update fixes the exact issue they reported)

**Example 3: SkillNotFollowed → Annotate**

Input:
```json
{
  "skill_id": "chrome/downloads",
  "reason": "seemed_wrong",
  "explanation": "Skill says ~/Downloads but files went to /tmp",
  "alternative_used": null
}
```

→ `read_skills(["chrome/downloads"])`
→ No previous annotations, 3 positives.
→ `annotate_skill(skill_id="chrome/downloads", annotation="Report: Downloads went to /tmp. Possibly environment-specific.")`

**Example 4: Learning → No action**

Input:
```json
{
  "type": "discovered",
  "scope": "os",
  "situation": "Copying files",
  "guidance": "Use Ctrl+C and Ctrl+V",
  "confidence": "high"
}
```

→ Basic knowledge, not worth storing.
→ No action.

**Example 5: Learning → Merge**

Input:
```json
{
  "type": "friction",
  "scope": "gimp",
  "situation": "Adding transparency support to layer",
  "guidance": "Right-click layer → Add Alpha Channel. Required before Color to Alpha.",
  "confidence": "high",
  "steps_wasted": 4
}
```

→ `fetch_similar_skills("transparency alpha channel gimp")`
→ Found `gimp/color-to-alpha` and `gimp/alpha-channel` — these overlap.
→ `merge_skills(source_skill_id="gimp/alpha-channel", target_skill_id="gimp/color-to-alpha", ...)`

---

### Principles

- **One write action per input** — read tools can be called multiple times, write tools only once
- **Explore first** — check similar skills before creating
- **Conservative when uncertain** — annotate rather than update
- **Patterns matter** — multiple reports justify action, single report justifies annotation
- **Concrete only** — don't store vague or basic guidance
- **Preserve knowledge** — prefer update/merge over delete
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
            instructions=_SYSTEM_PROMPT_LEARNER,
            previous_response_id=previous_response_id,
            tools=self.tools.get_tools(),
            tool_choice="auto",
        )
        self.last_response_id = response.id
        return response
    
    def call_llm(self, obj: BaseModel) -> tuple[list[dict], TokenUsage]:
        tool_called = True
        token_usage = TokenUsage()
        tool_results = []
        history = []
        previous_response_id = None

        while tool_called:
            response = self._make_call(
                prompt=json.dumps(obj.model_dump_json(indent=4)), 
                tool_results=tool_results, 
                previous_response_id=previous_response_id
            )
            previous_response_id = response.id
            token_usage += TokenUsage.from_response(response)
            tool_calls = get_tool_calls_from_response(response)
            tool_called = len(tool_calls) > 0

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

        history.append({
            "final_response": response.output_text
        })
        return history, token_usage
    
    def learn(self, reviews: list[SkillReview], learnings: list[Learning]) -> list[dict]:
        reviews_to_process = [self.manage_skill_review(r) for r in reviews]
        reviews_to_process = list(filter(lambda r: r is not None, reviews_to_process))

        learning_history = []
        for review in reviews_to_process:
            hist, token_usage = self.call_llm(review)
            learning_history.append({
                "review": review.model_dump_json(indent=4),
                "skill_manager": hist,
                "token_usage": token_usage.model_dump_json(indent=4)
            })

        for learning in learnings:
            hist, token_usage = self.call_llm(learning)
            learning_history.append({
                "learning": learning.model_dump_json(indent=4),
                "skill_manager": hist,
                "token_usage": token_usage.model_dump_json(indent=4)
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
            if review.corrected_guidance is not None:
                return review
            else:
                skill.annotate(f"Negative review [{review.issue_type}]: {review.what_went_wrong}")

        
        elif isinstance(review, SkillNotFollowed):
            if review.reason == "seemed_wrong":
                return review
            if review.reason == "chose_alternative":
                skill.annotate(f"Skill not followed [{review.reason}]: {review.explanation}")
