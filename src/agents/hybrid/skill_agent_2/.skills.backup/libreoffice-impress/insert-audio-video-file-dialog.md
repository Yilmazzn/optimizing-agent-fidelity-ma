---
annotations: []
description: 'Insert audio/video in Impress: file dialog quirks + confirm insertion
  on slide'
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: insert-audio-video-file-dialog
---

## Insert audio/video when the file dialog won’t proceed
1. Go to **Insert > Audio or Video…**.
2. In the file picker, navigate to the folder.
3. **Single-click the media file** so the row is highlighted (and/or its name appears in the **File name** box).
4. Click **Open**.

Tip: **Double-click** the file to select + insert in one step. If a folder/location is focused (not a file), **Open** may appear to do nothing.

## Confirm the insert succeeded (don’t delete it by accident)
- After insertion, Impress places a small **media/speaker icon (object)** on the current slide.
- If you immediately press **Delete**, you remove that inserted audio object from the slide (making it look like the insert failed).
- To restore it, re-insert via **Insert > Audio or Video…**.