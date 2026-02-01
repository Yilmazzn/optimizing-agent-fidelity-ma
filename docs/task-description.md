# Skill-Based Learning for Computer Use Agents

## Overview

A learning framework where a capable model generates detailed, actionable skills from its own traces. The primary objective is **knowledge distillation**: enabling smaller, less capable models to achieve higher success rates by providing them with explicit procedural knowledge. Optimization of the capable model itself is a secondary benefit.

---

## What Skills Are For

Skills are for **non-obvious knowledge**—things a capable model might figure out eventually but would waste steps on.

**Not skills:**
- "Click buttons to interact with them"
- "Scroll to see more content"
- "Type in text fields"

**Skills:**
- "Color to Alpha is at Filters > Color, not in the toolbox"
- "Ctrl+G opens cell navigation in LibreOffice Calc"
- "Site permissions are accessible via the lock icon"

The agent already knows *how* to use a computer. Skills tell it *where things are* and *what works best*.

---

## Core Loop

```
┌─────────────────────────────────────────────────────────────┐
│  Capable Agent runs task, generates trace                   │
│  - Can request skills from skillbook during run             │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Reflection Phase (two parallel agents)                     │
│  - Skill Reflector: evaluates retrieved skills              │
│  - Trajectory Learner: extracts new guidance                │
│  Output: markdown (preserves context cache)                 │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Split markdown into individual learnings/reviews           │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  For each learning/review (sequentially):                   │
│                                                             │
│    Skillbook Manager                                        │
│    - Fetches similar skills                                 │
│    - Decides action + outputs content                       │
│                     ↓                                       │
│    Apply to skillbook immediately                           │
│    (next iteration sees updated state)                      │
└─────────────────────────────────────────────────────────────┘
```

---

## The Computer Use Agent

Receives screenshots and executes tools to interact with the computer in a multi-turn fashion until task completion. During execution, the agent can request skills from the skillbook. Skills are learnings from past runs—the agent doesn't have to follow them blindly, but they provide guidance.

### Runtime Skill Access

The agent always has in context:
- Domain list with brief descriptions
- Knowledge that it can request skills anytime

```markdown
## Skillbook

You have access to a skillbook with guidance for various applications.

Domains:
- **os**: System interactions (file dialogs, clipboard, windows)
- **gimp**: Image editing
- **chrome**: Browser
- **libreoffice-calc**: Spreadsheets

Use `read_domain_index(domain)` to see available skills.
Use `read_skill(domain, skill)` to read a skill.

Request skills when you encounter non-obvious UI or need specific guidance.
You can request skills anytime—before starting or mid-task.
```

### Skill Retrieval Tools

```python
read_domain_index(domain: Literal["os", "gimp", "chrome", "libreoffice-calc", ...])
```
Returns the INDEX.md for that domain—list of available skills with descriptions.

```python
read_skill(domain: Literal["os", "gimp", ...], skill: str)
```
Returns the full skill content.

Domain parameter is constrained to known domains (enables constrained generation). Skill parameter is free-form (agent has just seen the index).

### Runtime Flow

```
┌─────────────────────────────────────────────────────────────┐
│  Agent starts task                                          │
│                                                             │
│  Always in context:                                         │
│  - Domain list with brief descriptions                      │
│  - Knowledge that it can request skills anytime             │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Agent reasons: "I'll be working in GIMP, let me see        │
│  what skills are available"                                 │
│                                                             │
│  → read_domain_index('gimp')                                │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Agent sees skill list with descriptions                    │
│                                                             │
│  → read_skill('gimp', 'transparency')                       │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Agent works on task                                        │
│                                                             │
│  Mid-task: "I need to export this, let me get that skill"   │
│  → read_skill('gimp', 'export')                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Skillbook Structure

Flat hierarchy—one folder per domain, no nesting within domains.

```
skillbook/
├── DOMAINS.md                      # Always in context (brief)
│
├── os/
│   ├── INDEX.md
│   ├── file-dialogs.md
│   ├── clipboard.md
│   └── window-management.md
│
├── gimp/
│   ├── INDEX.md
│   ├── transparency.md
│   ├── layers.md
│   ├── export.md
│   └── selection.md
│
├── chrome/
│   ├── INDEX.md
│   ├── permissions.md
│   └── settings.md
│
└── libreoffice-calc/
    ├── INDEX.md
    ├── cell-selection.md
    ├── formulas.md
    └── charts.md
```

### DOMAINS.md (Always in Context)

Brief domain descriptions only. Kept minimal to avoid bloating system prompt.

```markdown
## Skillbook

Domains:
- **os**: System interactions (file dialogs, clipboard, windows)
- **gimp**: Image editing
- **chrome**: Browser
- **libreoffice-calc**: Spreadsheets
```

### INDEX.md Format

Verbose skill descriptions to help agent decide relevance. Auto-generated programmatically from skill files.

```markdown
# GIMP

Image editing application for photo manipulation, digital art, and graphic design.

## Skills

- **transparency**: Making backgrounds transparent, removing solid colors, using Color to Alpha, adding alpha channels to layers

- **layers**: Creating and managing layers, layer ordering, visibility, merging layers, layer groups, layer masks

- **export**: Saving as PNG/JPEG/WebP, export vs save distinction, preserving transparency in exports, quality settings

- **selection**: Selection tools (rectangle, ellipse, free, fuzzy), selection modes, feathering, select by color, grow/shrink selection

- **color-tools**: Color adjustments, curves, levels, hue-saturation, color balance, desaturate, invert

- **transform**: Scaling, rotating, flipping, perspective, cropping, canvas resize
```

Descriptions are **action-oriented**—they describe what the agent can accomplish, not just topics.

### Skill File Format

```markdown
# Transparency in GIMP

## Trigger
- **Scope**: gimp
- **Situation**: Making colors or backgrounds transparent

## Guidance

### Color to Alpha
Use Filters > Color > Color to Alpha to make a specific color transparent.

1. Select the target layer in the Layers panel
2. Go to Filters > Color > Color to Alpha
3. Click the color preview to select the color
4. Adjust threshold if edges appear rough
5. Click OK

Export as PNG to preserve transparency.

### Alpha Channel
To add transparency support to a layer:
1. Right-click layer in Layers panel
2. Select "Add Alpha Channel"

## Metadata
- **Positive**: 12
- **Negative**: 1
- **Neutral**: 3
- **Last validated**: 2024-01-15
- **Annotations**: 
  - "Threshold slider can be finicky with gradients—investigate"
```

---

## Reflection Phase

Two separate agents operate on the completed trace. Separation ensures:
- Different context requirements (Skill Reflector needs skill text; Trajectory Learner works better without anchoring on existing skills)
- Different failure modes (each can be tuned independently)
- Cleaner downstream (reflections update existing skills; new guidance creates new skills)

Both agents output **free-form markdown** (not structured JSON) to preserve context cache.

---

### Agent 1: Skill Reflector

**Purpose**: Evaluate how retrieved skills impacted the trajectory.

**Input**: 
- Full trace
- Skills that were retrieved during the run

**Output**: For each skill, a reflection covering impact, reasoning, and feedback.

#### Prompt

```markdown
## Reflect on the skills used in this trajectory

During this task, the following skills were retrieved from the skillbook:

{skills}

Review each skill and evaluate how it impacted the trajectory.

For each skill, assess:
- **Followed**: Did the agent follow this skill's guidance? (yes | no | partially)
- **Impact**: Did this skill help the agent succeed (positive), mislead or cause friction (negative), or have no meaningful effect (neutral)?
- **Reason**: Why did it have this impact? Tie your explanation to what actually happened in the trace.
- **Feedback**: What would make this skill better? Concrete suggestions. Write "none" if the skill worked well as-is.

### Output Format

For each skill:

**Skill**: <skill identifier>
**Followed**: yes | no | partially
**Impact**: positive | negative | neutral
**Reason**: <brief explanation tied to the trace>
**Feedback**: <concrete suggestion, or "none">

---

### Guidelines

- **Be specific**: Reference what actually happened in the trace
- **Be constructive**: Feedback should suggest improvements
- **Judge impact by outcome**: 
  - Positive = skill contributed to success
  - Negative = skill caused confusion, errors, or wasted steps
  - Neutral = skill had no meaningful effect (irrelevant to task, or agent already knew this)
- **Include all skills**: Every retrieved skill needs a reflection

If no skills were retrieved, write:

No skills were used in this trajectory.
```

#### Example Output

```markdown
**Skill**: gimp/transparency
**Followed**: yes
**Impact**: positive
**Reason**: Agent needed to make background transparent. Skill provided exact menu path. Agent followed it directly and succeeded on first attempt.
**Feedback**: none

---

**Skill**: libreoffice-calc/cell-selection
**Followed**: yes
**Impact**: negative
**Reason**: Skill recommended Ctrl+G for range selection, but this opened "Go To" dialog instead of allowing range input. Agent had to close dialog and find alternative approach.
**Feedback**: Ctrl+G behavior may differ across LibreOffice versions. Verify correct shortcut or provide version-specific guidance.

---

**Skill**: chrome/permissions
**Followed**: no
**Impact**: neutral
**Reason**: Skill was retrieved but task didn't require modifying permissions. Skill wasn't used.
**Feedback**: Trigger context may be too broad—consider narrowing "situation" to avoid irrelevant retrieval.
```

#### Downstream Use

- Metadata counts (positive/negative/neutral) updated programmatically
- Reviews with feedback passed to Skillbook Manager

---

### Agent 2: Trajectory Learner

**Purpose**: Extract new guidance from the trajectory that could help a less capable agent.

**Input**: Full trace only (no existing skills—avoids anchoring)

**Output**: Free-form markdown with learnings separated by `---`

#### Prompt

```markdown
## Reflect on this trajectory

You have just completed a task. Review the trajectory above and extract any guidance that could help a less capable agent succeed in similar situations.

Look for:
1. **Friction moments**: Where did you struggle, retry, or take multiple attempts before succeeding? What knowledge would have helped you succeed faster?
2. **Discovered knowledge**: Did you learn or notice anything useful that wasn't obvious beforehand?

For each learning, write a section covering:
- **What happened**: Brief factual description from the trace
- **Source**: Was this a friction (struggled then succeeded) or discovered (noticed without struggling)?
- **Why it matters**: What made it hard (friction) or how you discovered it
- **Scope**: Where does this apply? (`general`, `os`, or application name like `gimp`, `chrome`)
- **Situation**: When is this relevant? Describe the general context—not task-specific
- **Guidance**: Clear, actionable instructions—what TO do, not what to avoid
- **Confidence**: How certain are you? (low / medium / high)
- **Steps wasted**: If friction, roughly how many actions were spent before resolution

Separate each learning with `---`

If there are no meaningful learnings from this trajectory, write:

No learnings extracted.

### Guidelines

- **Be general**: Guidance should help with many tasks, not just this specific one
- **Be positive**: Describe what to do, not what to avoid
- **Be honest**: Only extract learnings where you're reasonably confident
- **Be selective**: Not every trace has learnings—it's fine to extract nothing
```

#### Example Output

```markdown
**What happened**: Searched toolbox, Layer menu, and tried eraser tool over 7 actions before finding transparency feature in Filters menu

**Source**: friction

**Why it matters**: The feature is named "Color to Alpha" and located under Filters, not "transparency" in the toolbox where image manipulation tools are expected

**Scope**: gimp

**Situation**: Making colors or backgrounds transparent

**Guidance**: Use Filters > Color > Color to Alpha. Select the target layer first, then choose the color to make transparent. Adjust threshold for rough edges. Export as PNG to preserve transparency.

**Confidence**: high

**Steps wasted**: 7

---

**What happened**: Used address bar lock icon to access site permissions directly

**Source**: discovered

**Why it matters**: Found while adjusting camera permissions for video call—faster than navigating through settings

**Scope**: chrome

**Situation**: Viewing or modifying site-specific permissions

**Guidance**: Click the lock/tune icon left of the URL, then select "Site settings". Changes apply immediately.

**Confidence**: medium

**Steps wasted**: n/a
```

---

## Skillbook Manager

**Purpose**: Maintain a clean, accurate, and helpful skillbook by processing learnings and reviews one at a time.

**Key Design**: Sequential processing with immediate application. Each call sees the updated skillbook state from previous calls.

### Flow

```
┌─────────────────────────────────────────────────────────────┐
│  Input: Single learning OR single review                    │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Skillbook Manager                                          │
│                                                             │
│  Tools:                                                     │
│  - fetch_similar_skills(domain, situation)                  │
│  - read_skill(domain, skill_name)                           │
│                                                             │
│  Reasons about:                                             │
│  - Is this covered by existing skill?                       │
│  - Does this extend an existing skill?                      │
│  - Is this new knowledge?                                   │
│  - Is this contradicting existing guidance?                 │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Output: Structured decision                                │
│  (create/update/annotate/delete/discard with content)       │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Programmatic: Apply action immediately                     │
│  - Write/update/delete skill file                           │
│  - Regenerate INDEX.md for domain                           │
│  - Update metadata counts                                   │
└─────────────────────────────────────────────────────────────┘
```

### Tools

```python
fetch_similar_skills(domain: str, situation: str) -> str
```
Find skills in the given domain related to the situation. Returns full content of top matches.

```python
read_skill(domain: str, skill_name: str) -> str
```
Read the full content of a specific skill.

### Output Schema

```python
class CreateDecision(BaseModel):
    """Decision to create a new skill."""
    
    action: Literal["create"] = "create"
    source_material: str = Field(..., description="The learning/guidance this decision applies to")
    reason: str = Field(..., description="Why a new skill should be created")
    domain: str = Field(..., description="Domain for the new skill (e.g., 'gimp', 'os')")
    skill_name: str = Field(..., description="Name for the new skill (e.g., 'color-to-alpha')")
    skill_content: str = Field(..., description="Complete skill content in standard format")


class UpdateDecision(BaseModel):
    """Decision to update an existing skill."""
    
    action: Literal["update"] = "update"
    source_material: str = Field(..., description="The learning/review this decision applies to")
    reason: str = Field(..., description="Why this skill should be updated")
    target_skill: str = Field(..., description="Skill to update: 'domain/skill-name'")
    skill_content: str = Field(..., description="Complete updated skill content")


class AnnotateDecision(BaseModel):
    """Decision to add an annotation to an existing skill."""
    
    action: Literal["annotate"] = "annotate"
    source_material: str = Field(..., description="The learning/review this decision applies to")
    reason: str = Field(..., description="Why an annotation is appropriate")
    target_skill: str = Field(..., description="Skill to annotate: 'domain/skill-name'")
    annotation: str = Field(..., description="The note to add for future review")


class DeleteDecision(BaseModel):
    """Decision to delete an existing skill."""
    
    action: Literal["delete"] = "delete"
    source_material: str = Field(..., description="The review/feedback that triggered this deletion")
    reason: str = Field(..., description="Why this skill should be removed")
    target_skill: str = Field(..., description="Skill to delete: 'domain/skill-name'")


class DiscardDecision(BaseModel):
    """Decision to discard a learning/review (no action needed)."""
    
    action: Literal["discard"] = "discard"
    source_material: str = Field(..., description="The learning/review being discarded")
    reason: str = Field(..., description="Why this should be discarded")


DecisionOutput = Union[CreateDecision, UpdateDecision, AnnotateDecision, DeleteDecision, DiscardDecision]
```

### Prompt

```markdown
## Skillbook Manager

You are the Skillbook Manager. Your job is to decide what action to take based on a single incoming learning or skill review, and output the complete result.

### Input Types

**Learning** (from Trajectory Learner):
New guidance extracted from an agent run. Contains what happened, scope, situation, guidance, and confidence.

**Review** (from Skill Reflector):
Feedback on an existing skill. Contains the skill ID, whether it was followed, impact (positive/negative/neutral), and suggestions.

### Your Task

1. Identify the scope/domain and situation from the input
2. Use `fetch_similar_skills(domain, situation)` to find related skills
3. If reviewing a specific skill, use `read_skill(domain, skill_name)` to see its current content
4. Decide the appropriate action and provide complete output

### Decision Guidelines

**create** — when:
- New knowledge that no existing skill covers
- High or medium confidence
- Clearly actionable guidance
- Output: complete skill content in standard format

**update** — when:
- Learning extends or improves an existing skill
- Review feedback points to a concrete fix
- High confidence that the change is correct
- Output: complete updated skill content

**annotate** — when:
- Uncertain if change is needed
- Low confidence learning
- Feedback suggests possible issue but needs verification
- Output: annotation text only

**delete** — when:
- Skill is clearly harmful (consistent negative reviews)
- Skill is obsolete or consistently wrong
- Use sparingly—prefer annotate if uncertain

**discard** — when:
- Learning is already fully covered by existing skill
- Too low confidence to act on
- Not actionable (vague, unclear)
- Review has no feedback and positive/neutral impact

### Skill Format

When creating or updating skills, use this format:

```markdown
# {Skill Title}

## Trigger
- **Scope**: {domain}
- **Situation**: {when this applies}

## Guidance

{Clear, actionable instructions with steps}

## Metadata
- **Positive**: 0
- **Negative**: 0
- **Neutral**: 0
- **Last validated**: {date}
- **Annotations**: []
```

### Principles

- **Be conservative**: When uncertain, annotate rather than update or delete
- **Avoid duplicates**: Check similar skills carefully before creating
- **Preserve knowledge**: Prefer update over delete when possible
- **Be concise**: Skills should be actionable, not verbose
```

---

## Programmatic Steps

### After Each Skillbook Manager Decision

```python
def apply_decision(decision: DecisionOutput):
    if isinstance(decision, CreateDecision):
        # Write new skill file
        write_file(f"skillbook/{decision.domain}/{decision.skill_name}.md", decision.skill_content)
        # Regenerate index
        regenerate_index(decision.domain)
        
    elif isinstance(decision, UpdateDecision):
        domain, skill_name = decision.target_skill.split("/")
        # Overwrite skill file
        write_file(f"skillbook/{domain}/{skill_name}.md", decision.skill_content)
        # Regenerate index
        regenerate_index(domain)
        
    elif isinstance(decision, AnnotateDecision):
        domain, skill_name = decision.target_skill.split("/")
        # Append annotation to skill metadata
        append_annotation(f"skillbook/{domain}/{skill_name}.md", decision.annotation)
        
    elif isinstance(decision, DeleteDecision):
        domain, skill_name = decision.target_skill.split("/")
        # Delete skill file
        delete_file(f"skillbook/{domain}/{skill_name}.md")
        # Regenerate index
        regenerate_index(domain)
        
    elif isinstance(decision, DiscardDecision):
        # Log reason, no action
        log_discard(decision.source_material, decision.reason)
```

### Index Regeneration

```python
def regenerate_index(domain: str):
    skills = []
    for file in glob(f"skillbook/{domain}/*.md"):
        if file.endswith("INDEX.md"):
            continue
        content = read_file(file)
        skill_name = extract_skill_name(file)
        situation = extract_situation(content)
        skills.append((skill_name, situation))
    
    index_content = generate_index_markdown(domain, skills)
    write_file(f"skillbook/{domain}/INDEX.md", index_content)
```

### Metadata Updates (from Skill Reflector)

```python
def update_skill_metadata(skill_id: str, impact: str):
    domain, skill_name = skill_id.split("/")
    skill_path = f"skillbook/{domain}/{skill_name}.md"
    
    # Increment appropriate counter
    if impact == "positive":
        increment_metadata(skill_path, "Positive")
    elif impact == "negative":
        increment_metadata(skill_path, "Negative")
    elif impact == "neutral":
        increment_metadata(skill_path, "Neutral")
    
    update_last_validated(skill_path)
```

---

## Signals for Identifying Learnable Moments

Since there's no explicit success/failure feedback, the Trajectory Learner uses heuristics:

| Signal | Indicates |
|--------|-----------|
| Agent retried an action multiple times | Friction—probably a better way exists |
| Agent scrolled/searched extensively | Missing knowledge about locations |
| Agent corrected itself mid-trace | Learned something that could be known upfront |
| Agent took a circuitous path | Workflow optimization opportunity |

---

## Why Sequential Processing

The Skillbook Manager processes learnings/reviews one at a time with immediate application:

1. **Simpler reasoning** — Manager focuses on one decision
2. **Self-correcting** — If Learning 1 creates a skill, Learning 2 sees it and can update instead of duplicate
3. **Easier debugging** — Trace each decision independently
4. **Graceful failure** — One bad decision doesn't break everything
5. **Skillbook consistency** — Each call sees current state
