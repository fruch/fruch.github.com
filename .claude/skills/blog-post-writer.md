---
name: blog-post-writer
description: >
  Multi-phase blog writing assistant for Fruch's Blog. Phases: brainstorm (mix raw topics),
  outline (AI-assisted structure), write (guided session), picture (AI image suggestions).
  Invoke with: /blog-post-writer [phase] — where phase is brainstorm, outline, write, or picture.
user_invocable: true
---

# Blog Post Writer

A guided blog writing workflow for Fruch's Blog. Each phase builds on the previous one.

## How to Use

Invoke with one of these phases:
- `/blog-post-writer brainstorm` — Dump raw topics and ideas, get refined post candidates
- `/blog-post-writer outline` — Pick a topic, build a structured outline
- `/blog-post-writer write` — Guided writing session for a specific post
- `/blog-post-writer picture` — Generate AI image prompt suggestions for a post

## Style Reference

Before ANY phase, read `.claude/skills/blog-style-guide.md` using the Read tool. All output must align with the voice, tone, and structure defined there.

---

## Phase 1: Brainstorm (`brainstorm`)

**Goal:** Turn raw, unstructured topic ideas into concrete blog post candidates.

### Instructions

1. **Ask the user for raw input.** Prompt them to dump everything — keywords, half-ideas, links, frustrations, things they learned recently, conference talks they liked, repos they're excited about. No filtering, no judgment. Example prompt:

   > "Dump everything you've been thinking about lately — topics, tools, rants, links, shower thoughts. Don't worry about structure. I'll help you mix and match."

2. **Cross-pollinate the ideas.** Look for intersections between topics. The best blog posts come from combining two things that don't obviously go together (e.g., "AI + a 4-year-old abandoned repo" became the Coodie post). For each intersection, generate a candidate post idea.

3. **For each candidate, produce:**
   - A catchy working title (aligned with the blog's punny/playful title style)
   - A one-liner description (what the reader walks away with)
   - The structure pattern it fits best (from the style guide: problem-solution, code review, story-driven, or event recap)
   - Estimated depth: quick tip (~500 words), standard post (~1500 words), or deep dive (~3000+ words)
   - Key ingredients: what code, tools, or experiences would be needed

4. **Present the candidates as a numbered list** and ask the user to pick favorites, combine ideas, or add more raw input for another round.

5. **Save the brainstorm session** to `_drafts/brainstorm-YYYY-MM-DD.md` with YAML front matter:

   ```yaml
   ---
   type: brainstorm
   date: YYYY-MM-DD
   raw_input: |
     (user's raw dump)
   ---
   ```

   Followed by the numbered candidate list.

---

## Phase 2: Outline (`outline`)

**Goal:** Take a chosen topic and build a structured outline with section headings, key points, and code snippet placeholders.

### Instructions

1. **Identify the topic.** Either:
   - The user specifies which brainstorm candidate to develop, OR
   - The user provides a new topic directly

2. **Read the style guide** (`.claude/skills/blog-style-guide.md`) and identify which structure pattern fits best.

3. **Build the outline** with:
   - **Title options** — suggest 3 title variations (punny, descriptive, provocative)
   - **Hook / opening** — 2-3 sentence opening that sets the scene (per the blog's conversational style)
   - **Section breakdown** — each `##` section with:
     - 1-2 sentence summary of what goes there
     - `[CODE]` placeholders where code snippets should go
     - `[SCREENSHOT]` placeholders where images might help
     - Key points to hit
   - **Closing** — suggested sign-off approach (humor, CTA, reflection)
   - **Front matter** — pre-filled YAML front matter with suggested category and tags

4. **Ask for user feedback.** Let them reorder sections, add/remove points, change the angle.

5. **Save the outline** to `_drafts/YYYY-MM-DD-slug.md` with status in front matter:

   ```yaml
   ---
   layout: post
   title: "Working Title"
   description: "Draft description"
   category: suggested-category
   tags: [tag1, tag2]
   status: outline
   ---
   ```

   The body contains the structured outline with placeholders.

---

## Phase 3: Write (`write`)

**Goal:** Guided writing session — work through the outline section by section, expanding placeholders into full prose and code.

### Instructions

1. **Load the draft.** Read the outline from `_drafts/YYYY-MM-DD-slug.md`.

2. **Read the style guide** for voice reference.

3. **Work section by section.** For each section in the outline:

   a. **Show the user the section plan** (from the outline) and ask:
      > "Ready to write the [section name] section? Here's what we planned: [summary]. Want to adjust anything before we start?"

   b. **Collaborative drafting:**
      - Ask the user for their raw thoughts / key points for this section
      - Draft the section in the blog's voice (casual, first-person, with code)
      - Present the draft and ask for feedback
      - Iterate until the user is happy

   c. **Code blocks:** When a `[CODE]` placeholder is reached:
      - Ask the user to paste or describe the code
      - Format it with proper fenced blocks and language identifier
      - Add brief inline commentary if the code isn't self-explanatory

   d. **Save progress** after each section — update the draft file in `_drafts/`

4. **Final assembly:**
   - Read through the complete post for flow and consistency
   - Check that the tone matches the style guide throughout
   - Suggest any transitions between sections that feel abrupt
   - Update front matter: set `status: draft` (or remove status for publishing)
   - Suggest moving to `_posts/YYYY-MM-DD-slug.md` when ready

5. **Pre-publish checklist:**
   - [ ] Title is catchy and accurate
   - [ ] Description is filled in (for SEO/social)
   - [ ] Tags and category are set
   - [ ] All `[CODE]` and `[SCREENSHOT]` placeholders are resolved
   - [ ] Links use reference style at bottom
   - [ ] No walls of text without breaks
   - [ ] Opening hooks the reader in 2-3 sentences
   - [ ] Closing has personality

---

## Phase 4: Picture (`picture`)

**Goal:** Generate AI image prompt suggestions that match the blog post's content and tone.

### Instructions

1. **Read the target post** (from `_drafts/` or `_posts/`).

2. **Analyze the post** for:
   - Core theme / metaphor
   - Technical tools or concepts featured
   - The emotional tone (humorous, reflective, energetic, etc.)
   - Any visual analogies mentioned in the text

3. **Generate 3-5 image prompt suggestions**, each with:
   - **Placement:** Where in the post it would go (hero image, mid-section, etc.)
   - **AI prompt:** A detailed prompt suitable for DALL-E, Midjourney, or similar tools. Include:
     - Visual style (e.g., "flat illustration", "isometric", "hand-drawn sketch", "retro pixel art")
     - Subject description
     - Color palette suggestions
     - Mood/atmosphere
   - **Alt text:** Accessible description for the `alt` attribute
   - **Why this works:** Brief explanation of how it relates to the post content

4. **Style preferences for this blog:**
   - Prefer illustrations over photorealistic images (matches the dev blog aesthetic)
   - Tech-themed but not generic stock-photo style
   - Humor/personality is a plus (matches the blog voice)
   - Keep it simple — one clear concept per image
   - Suggest dimensions: 1200x630px for hero/social cards, 800x400px for inline

5. **Output format:**

   ```markdown
   ### Image Suggestion 1: [placement]

   **Prompt:** "..."

   **Alt text:** "..."

   **Why:** ...
   ```

6. **After presenting suggestions**, ask the user which ones to pursue and whether they want variations or adjustments.
