---
annotations:
- 'Skill not followed [chose_alternative]: The task was solved more directly by editing
  the presentation/drawing text styles via the Styles sidebar (F11) rather than entering
  Master Slide view.'
- 'Skill not followed [chose_alternative]: Background was changed directly in the
  Sidebar (Properties ▸ Slide ▸ Background) for the current slide, so entering Master
  Slide view wasn’t necessary.'
description: Change slide backgrounds/transitions + master slide objects in Impress
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 2
name: master-slide-elements
---

## Before you change slide properties
- For **Background/Orientation**: click an **empty area of the slide** (so you’re editing the slide/page, not a text box).
- For **Transitions**: select the slide’s **thumbnail** in the left Slides pane first.

## Case 1: Set background color for one (or a few) slides (Sidebar)
1. Click an empty area of the target slide.
2. If needed: **View ▸ Sidebar**.
3. Sidebar ▸ **Properties ▸ Slide**.
4. **Background**: change **None → Color**.
5. Pick the color.

### Apply to multiple slides
1. **View ▸ Slide Sorter**.
2. Ctrl/Shift-select slides.
3. Sidebar ▸ **Properties ▸ Slide ▸ Background** → **Color**.

## Case 2: Change slide orientation (portrait/landscape)
1. Click an empty area of the slide.
2. Sidebar ▸ **Properties** → **Orientation** → **Portrait** or **Landscape**.
3. If prompted, choose whether to **scale/fit contents**.

Fallback if Orientation isn’t visible: **Slide ▸ Slide Properties…** (wording varies).

## Case 3: Apply a transition to one slide
1. In the left **Slides** thumbnail pane, click the slide you want.
2. Open: **Slide ▸ Slide Transition**.
3. In the right Sidebar panel that opens, click a transition (it applies immediately).

If you don’t see the panel: **View ▸ Sidebar**, then re-run **Slide ▸ Slide Transition**.

## Case 4: Set background for all slides (Master Slide)
Use this for deck-wide backgrounds/placeholders.
1. Go to **View ▸ Master Slide**.
2. In the left pane, click a **master** thumbnail.
3. Set background: **Slide ▸ Slide Properties… ▸ Background** (wording varies) → choose fill/color/image → **OK**.
4. Repeat for **each master** thumbnail (files can use multiple masters).
5. Click **Close Master View**.

## Case 5: Format footer/date/slide-number placeholders across the whole deck
If formatting “does nothing”, you may be formatting the frame, not the placeholder text.
1. Go to **View ▸ Master Slide**.
2. Click the **Slide number / Date / Footer** placeholder.
3. Enter text edit mode (double‑click, or **F2**) so the caret appears.
4. Select the placeholder text (often **Ctrl+A** inside that box).
5. Apply formatting via:
   - **Format ▸ Character… ▸ Font Effects** → **Font color** (reliable), or
   - Sidebar **Properties ▸ Character** → **Font Color**.
6. **Close Master View**.

If only some slides change: the file uses **multiple masters/layouts**—repeat on each master in use.

## Case 6: Make a slide truly blank (hide master graphics on that slide)
When “Blank layout” still shows logo/footer/slide number:
1. Select the slide.
2. Sidebar ▸ **Properties ▸ Layouts** → choose **Blank**.
3. Sidebar ▸ **Properties ▸ Master Slide**:
   - Uncheck **Master Background**
   - Uncheck **Master Objects**

### Apply to multiple slides
Use **View ▸ Slide Sorter**, multi-select slides, then toggle the same checkboxes.