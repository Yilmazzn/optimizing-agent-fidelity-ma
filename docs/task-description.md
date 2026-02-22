# Skill-Based Learning for Computer Use Agents

## Overview

A learning framework where a capable model generates detailed, actionable skills from its own traces. The primary objective is **knowledge distillation**: enabling smaller, less capable models to achieve higher success rates by providing them with explicit procedural knowledge.

---

## What Skills Are For

Skills are for **non-obvious knowledge**—things a capable model might figure out eventually but would waste steps on.

**Not skills:**
- "Click buttons to interact with them"
- "Scroll to see more content"
- "Use Ctrl+C to copy"

**Skills:**
- "Color to Alpha is at Filters > Color, not in the toolbox"
- "Ctrl+G opens cell navigation in LibreOffice Calc"
- "Site permissions are accessible via the lock icon"

---

## Core Loop

```
┌─────────────────────────────────────────────────────────────┐
│  Capable Agent runs task, generates trace                   │
│  - Can request skills from skillbook during run             │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Trajectory Reflector                                       │
│  - Reviews used skills                                      │
│  - Extracts new learnings                                   │
│  Output: TrajectoryReflection (structured)                  │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Programmatic Handler                                       │
│  - Updates metrics for all reviews                          │
│  - Filters which reviews/learnings need agent processing    │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Skill Manager Agent (for filtered items)                   │
│  - Processes reviews and learnings one at a time            │
│  - Uses tools to read/write skillbook                       │
│  - Decides: create / update / merge / annotate / delete     │
└─────────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Periodic Cleanup                                           │
│  - Flags negative-heavy skills                              │
│  - Finds duplicate candidates                               │
│  - Identifies low follow-rate skills                        │
│  - Passes to Skill Manager for resolution                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Skillbook Structure

Flat hierarchy—one folder per domain, no nesting within domains.

```
skillbook/
├── DOMAINS.md                      # Always in agent context (brief)
│
├── os/
│   ├── INDEX.md
│   ├── file-dialogs.md
│   └── clipboard.md
│
├── gimp/
│   ├── INDEX.md
│   ├── transparency.md
│   ├── layers.md
│   └── export.md
│
├── chrome/
│   ├── INDEX.md
│   ├── permissions.md
│   └── settings.md
│
└── libreoffice-calc/
    ├── INDEX.md
    ├── cell-navigation.md
    └── formulas.md
```

### Skill File Format

```markdown
## Situation

{When this guidance applies — general context, not task-specific}

## Guidance

{Concrete, actionable steps. Numbered for procedures.}

## Annotations

- {notes from previous reviews, or "None"}
```

### Skill Metadata (stored separately or in-memory)

```python
class SkillMetrics(BaseModel):
    times_requested: int = 0
    times_followed: float = 0  # Can be 0.5 for "partially"
    positive_impact: int = 0
    negative_impact: int = 0
    neutral_impact: int = 0
    
    @property
    def times_not_followed(self) -> float:
        return self.times_requested - self.times_followed
```

---

## Trajectory Reflector

Single unified reflector that outputs both skill reviews and new learnings.

### Output Schema

```python
from pydantic import BaseModel, Field
from typing import Literal


# === Skill Reviews ===

class SkillPositive(BaseModel):
    """Skill was followed and helped succeed."""
    skill_id: str
    followed: Literal["yes", "partially"]
    impact: Literal["positive"] = "positive"
    what_helped: str = Field(description="How the skill contributed to success")


class SkillNegative(BaseModel):
    """Skill was followed but caused problems."""
    skill_id: str
    followed: Literal["yes", "partially"]
    impact: Literal["negative"] = "negative"
    issue_type: Literal["incorrect", "outdated", "incomplete", "unclear"]
    what_went_wrong: str
    corrected_guidance: str | None = Field(
        default=None,
        description="What actually worked, if discovered"
    )


class SkillNeutral(BaseModel):
    """Skill was followed but had minimal effect."""
    skill_id: str
    followed: Literal["yes", "partially"]
    impact: Literal["neutral"] = "neutral"
    reason: Literal["already_knew", "not_needed", "marginal"]
    suggested_improvement: str | None = Field(
        default=None,
        description="How the skill could be better"
    )


class SkillNotFollowed(BaseModel):
    """Skill was retrieved but not followed."""
    skill_id: str
    followed: Literal["no"] = "no"
    reason: Literal["irrelevant", "already_knew", "chose_alternative", "seemed_wrong"]
    explanation: str
    alternative_used: str | None = Field(
        default=None,
        description="What approach was used instead"
    )


SkillReview = SkillPositive | SkillNegative | SkillNeutral | SkillNotFollowed


# === New Learnings ===

class FrictionLearning(BaseModel):
    """Knowledge from struggling before succeeding."""
    type: Literal["friction"] = "friction"
    scope: str = Field(description="'general', 'os', or application name")
    situation: str = Field(description="When this applies (general, not task-specific)")
    guidance: str = Field(description="Actionable instructions with exact paths/shortcuts")
    confidence: Literal["low", "medium", "high"]
    steps_wasted: int = Field(ge=1)


class DiscoveredLearning(BaseModel):
    """Knowledge discovered without struggling."""
    type: Literal["discovered"] = "discovered"
    scope: str
    situation: str
    guidance: str
    confidence: Literal["low", "medium", "high"]


Learning = FrictionLearning | DiscoveredLearning


# === Unified Output ===

class TrajectoryReflection(BaseModel):
    skill_reviews: list[SkillReview] = Field(default_factory=list)
    new_learnings: list[Learning] = Field(default_factory=list)
```

### Reflector Prompt

```markdown
## Reflect on this trajectory

Review the trajectory you just completed and provide:
1. **Skill Reviews** — feedback on each skill that was retrieved
2. **New Learnings** — guidance that could help a less capable agent

### Skills Retrieved

{skills_section}

Note: You already saw the full content of these skills during the task.

---

## Part 1: Skill Reviews

Provide one review per skill listed above. If no skills were retrieved, return an empty list.

Focus on:
- Did following (or not following) the skill help or hurt?
- Was the guidance accurate and complete?
- What concrete improvement would make this skill better?

---

## Part 2: New Learnings

Extract guidance from:
- **Friction moments**: Where you struggled, retried, or wasted steps before succeeding
- **Discoveries**: Useful knowledge you noticed that wasn't obvious beforehand

**Worth extracting:**
- Non-obvious UI locations (menus, settings, hidden features)
- Keyboard shortcuts or faster workflows
- Gotchas or prerequisites that aren't intuitive
- Correct sequence of steps when order matters

**Not worth extracting:**
- Basic computer knowledge (clicking, scrolling, typing)
- Task-specific details that won't generalize
- Knowledge already covered by a retrieved skill (give feedback instead)

---

## Guidelines

- **Empty is fine**: Not every trajectory has learnings
- **Be general**: Guidance should help with many tasks
- **Be concrete**: Include exact menu paths, shortcuts, UI elements
- **Avoid duplicates**: Improve existing skills via feedback rather than creating new learnings
```

---

## Programmatic Review Handler

Handles metrics updates and filters what goes to the Skill Manager.

```python
class SkillLearner:
    def __init__(self, skill_book: SkillBook):
        self.skill_book = skill_book

    def learn(self, reviews: list[SkillReview], learnings: list[Learning]):
        # Process reviews, filter those needing agent attention
        reviews_to_process = [
            r for r in (self.manage_skill_review(review) for review in reviews)
            if r is not None
        ]
        
        # Pass to skill manager agent
        for review in reviews_to_process:
            self.skill_manager.process(review.model_dump())
        
        for learning in learnings:
            self.skill_manager.process(learning.model_dump())

    def manage_skill_review(self, review: SkillReview) -> SkillReview | None:
        """
        Updates metrics. Returns review if agent should process it.
        """
        skill = self.skill_book.get_skill(review.skill_id)
        skill.metrics.times_requested += 1

        if isinstance(review, SkillPositive):
            skill.metrics.positive_impact += 1
            skill.metrics.times_followed += 1
            return None  # No agent needed

        elif isinstance(review, SkillNeutral):
            skill.metrics.neutral_impact += 1
            skill.metrics.times_followed += 1 if review.followed == "yes" else 0.5
            if review.suggested_improvement is not None:
                return review  # Agent should evaluate improvement
            return None

        elif isinstance(review, SkillNegative):
            skill.metrics.negative_impact += 1
            skill.metrics.times_followed += 1 if review.followed == "yes" else 0.5
            if review.corrected_guidance is not None:
                return review  # Agent should update skill
            else:
                # No correction provided, just annotate
                skill.annotate(f"[{review.issue_type}] {review.what_went_wrong}")
                return None

        elif isinstance(review, SkillNotFollowed):
            if review.reason == "seemed_wrong":
                return review  # Agent should investigate
            if review.reason == "chose_alternative":
                skill.annotate(f"[{review.reason}] {review.explanation}")
                if review.alternative_used:
                    skill.annotate(f"[alternative] {review.alternative_used}")
            return None

        return None
```

### What Gets Passed to Skill Manager

| Review Type | Condition | Passed to Agent? |
|-------------|-----------|------------------|
| SkillPositive | Always | ❌ No |
| SkillNeutral | No suggestion | ❌ No |
| SkillNeutral | Has suggestion | ✅ Yes |
| SkillNegative | No corrected_guidance | ❌ No (annotated) |
| SkillNegative | Has corrected_guidance | ✅ Yes |
| SkillNotFollowed | irrelevant, already_knew | ❌ No |
| SkillNotFollowed | chose_alternative | ❌ No (annotated) |
| SkillNotFollowed | seemed_wrong | ✅ Yes |
| Learning | Always | ✅ Yes |

---

## Skill Manager Agent

Processes reviews and learnings one at a time using tools.

### Tools

```python
def get_tools(self) -> list[dict]:
    return [
        {
            "name": "fetch_similar_skills",
            "description": "Find related skills across all domains.",
            "parameters": {
                "type": "object",
                "properties": {
                    "situation": {
                        "type": "string",
                        "description": "Situation to match against"
                    }
                },
                "required": ["situation"]
            }
        },
        {
            "name": "read_skills",
            "description": "Read specific skills with full content, annotations, and metrics.",
            "parameters": {
                "type": "object",
                "properties": {
                    "skill_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Skill IDs to read"
                    }
                },
                "required": ["skill_ids"]
            }
        },
        {
            "name": "create_domain",
            "description": "Create a new domain for an application.",
            "parameters": {
                "type": "object",
                "properties": {
                    "domain": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["domain", "description"]
            }
        },
        {
            "name": "create_skill",
            "description": "Create a new skill.",
            "parameters": {
                "type": "object",
                "properties": {
                    "domain": {"type": "string"},
                    "skill_name": {"type": "string"},
                    "description": {"type": "string"},
                    "situation": {"type": "string"},
                    "guidance": {"type": "string"}
                },
                "required": ["domain", "skill_name", "description", "situation", "guidance"]
            }
        },
        {
            "name": "update_skill",
            "description": "Update an existing skill. Only provide fields to change.",
            "parameters": {
                "type": "object",
                "properties": {
                    "skill_id": {"type": "string"},
                    "description": {"type": "string"},
                    "situation": {"type": "string"},
                    "guidance": {"type": "string"}
                },
                "required": ["skill_id"]
            }
        },
        {
            "name": "merge_skills",
            "description": "Combine two overlapping skills. Source is deleted.",
            "parameters": {
                "type": "object",
                "properties": {
                    "source_skill_id": {"type": "string"},
                    "target_skill_id": {"type": "string"},
                    "description": {"type": "string"},
                    "situation": {"type": "string"},
                    "guidance": {"type": "string"}
                },
                "required": ["source_skill_id", "target_skill_id", "description", "situation", "guidance"]
            }
        },
        {
            "name": "annotate_skill",
            "description": "Add a note for future review.",
            "parameters": {
                "type": "object",
                "properties": {
                    "skill_id": {"type": "string"},
                    "annotation": {"type": "string"}
                },
                "required": ["skill_id", "annotation"]
            }
        },
        {
            "name": "delete_skill",
            "description": "Remove a skill. Use sparingly.",
            "parameters": {
                "type": "object",
                "properties": {
                    "skill_id": {"type": "string"}
                },
                "required": ["skill_id"]
            }
        }
    ]
```

### System Prompt

```markdown
## Skillbook Manager

You maintain a skillbook that helps less capable agents succeed at computer use tasks. You receive learnings and reviews one at a time, and decide what action (if any) to take.

---

### Input Types

**Learning**: New guidance extracted from a trajectory.
- `type`: "friction" or "discovered"
- `scope`: Application name or "general"/"os"
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

**SkillNotFollowed**: Skill was retrieved but agent didn't trust it.
- `skill_id`: The skill that was retrieved
- `reason`: "seemed_wrong"
- `explanation`: Why the agent didn't trust it
- `alternative_used`: (optional) What approach was used instead

---

### Tools

**Reading:**
- `fetch_similar_skills(situation)` — Searches across all domains
- `read_skills(skill_ids)` — Returns skills with content, annotations, metrics

**Writing:**
- `create_domain(domain, description)`
- `create_skill(domain, skill_name, description, situation, guidance)`
- `update_skill(skill_id, description?, situation?, guidance?)`
- `merge_skills(source_skill_id, target_skill_id, description, situation, guidance)`
- `annotate_skill(skill_id, annotation)`
- `delete_skill(skill_id)`

---

### Process

1. **Explore** (optional) — Use read tools to understand current state
2. **Decide** — Determine what action (if any) is needed
3. **Act** — Call at most ONE write tool, or take no action

Read tools can be called multiple times. Write tools only once per input.

---

### Decision Guidelines

**For Learnings:**

| Condition | Action |
|-----------|--------|
| No similar skill + confidence ≥ medium | `create_skill` |
| Similar skill exists + learning extends it | `update_skill` |
| Two skills overlap + learning bridges them | `merge_skills` |
| Low confidence | `annotate_skill` or no action |
| Guidance is basic | No action |
| Scope is new domain | `create_domain` then `create_skill` |

**For SkillNegative:**

| Condition | Action |
|-----------|--------|
| Correction is clear | `update_skill` |
| Conflicts with existing annotations | `annotate_skill` |
| Skill has many negatives | Consider `delete_skill` |

**For SkillNeutral:**

| Condition | Action |
|-----------|--------|
| Improvement is concrete | `update_skill` |
| Improvement is minor | `annotate_skill` |

**For SkillNotFollowed:**

| Condition | Action |
|-----------|--------|
| `alternative_used` is clearly better | `update_skill` |
| Unclear if better | `annotate_skill` |
| No `alternative_used` | `annotate_skill` |

---

### Using Annotations

- **Multiple similar complaints** → Pattern confirmed, safe to update
- **Conflicting information** → Be conservative, annotate
- **No annotations + first report** → Annotate, don't update yet

---

### What Makes Good Guidance

**Worth storing:**
- Non-obvious menu locations
- Specific shortcuts that differ from expected
- Required prerequisites
- Correct sequences when order matters

**Not worth storing:**
- Basic knowledge (Ctrl+C, clicking buttons)
- Vague guidance
- Task-specific details

---

### Principles

- **One write action per input**
- **Explore first** — check similar skills before creating
- **Conservative when uncertain** — annotate rather than update
- **Patterns matter** — multiple reports justify action
- **Concrete only** — don't store vague guidance
- **Preserve knowledge** — prefer update/merge over delete
```

---

## Periodic Cleanup

Runs periodically (e.g., every N trajectories) to maintain skillbook health.

### Cleanup Criteria

```python
@dataclass
class CleanupConfig:
    # Negative-heavy skills
    negative_threshold: int = 3
    positive_ratio_threshold: float = 0.3  # < 30% positive
    
    # Duplicate detection
    similarity_threshold: float = 0.85
    
    # Low follow-rate skills
    min_requests_for_follow_rate: int = 5
    follow_rate_threshold: float = 0.3  # < 30% followed
```

### Cleanup Tasks

```python
class SkillbookCleaner:
    def find_negative_heavy_skills(self) -> list[dict]:
        """Skills with high negative impact and low positive ratio."""
        ...
    
    def find_duplicate_candidates(self) -> list[dict]:
        """Pairs of skills with high similarity within a domain."""
        ...
    
    def find_low_follow_rate_skills(self) -> list[dict]:
        """Skills retrieved often but rarely followed."""
        ...
```

### Cleanup Task Types for Skill Manager

```markdown
**CleanupTask**: Maintenance task for problematic skills.
- `cleanup_type`: "negative_heavy" | "duplicates" | "low_follow_rate"
- `skill_id` or `skill_ids`: Skills to evaluate
- `context`: Metrics, annotations, similarity scores

**For `negative_heavy`:**
- If pattern is clear and fixable → `update_skill`
- If fundamentally flawed → `delete_skill`
- If unclear → `annotate_skill`

**For `duplicates`:**
- If truly overlapping → `merge_skills`
- If distinct use cases → No action

**For `low_follow_rate`:**
- Too broad? → `update_skill` to narrow situation
- Too obvious? → `delete_skill`
- Seems wrong? → Review annotations, consider update/delete
```

---

## Summary

| Component | Responsibility |
|-----------|---------------|
| **Computer Use Agent** | Runs tasks, requests skills at runtime |
| **Trajectory Reflector** | Reviews skills + extracts learnings (structured output) |
| **Programmatic Handler** | Updates metrics, filters what needs agent processing |
| **Skill Manager Agent** | Creates/updates/merges/annotates/deletes skills |
| **Periodic Cleanup** | Flags problematic skills for Skill Manager |

### What's Programmatic vs Agent

| Task | Handler |
|------|---------|
| Increment metrics | Programmatic |
| Annotate (no decision needed) | Programmatic |
| Delete obvious skills | Could be programmatic with thresholds |
| Create/update/merge skills | Agent |
| Evaluate conflicting info | Agent |
| Decide if learning is worth storing | Agent |