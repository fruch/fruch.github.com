# Blog Post Writer Skill — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Claude Code skill that guides the user through writing blog posts — from raw topic brainstorming, through AI-assisted structuring, to a guided writing session — all aligned with the blog's established voice and style.

**Architecture:** A multi-phase skill orchestrated as a single Claude Code skill file (`blog-post-writer`) with sub-commands for each phase: `brainstorm`, `outline`, `write`, and `picture`. A companion style-guide document captures the blog's tone, structure, and conventions. Each phase reads and writes to a working draft file under `_drafts/`.

**Tech Stack:** Claude Code skills (Markdown skill files), Jekyll `_drafts/` directory, Markdown front matter, AI image prompt generation.

---

## File Structure

| File | Responsibility |
|------|---------------|
| `.claude/skills/blog-post-writer.md` | Main skill file — routes to the correct phase |
| `.claude/skills/blog-style-guide.md` | Style reference extracted from existing posts — tone, structure, front matter conventions |
| `_drafts/` | Jekyll drafts directory — working area for posts in progress |

---

### Task 1: Create the Blog Style Guide

**Files:**
- Create: `.claude/skills/blog-style-guide.md`

This document captures the writing DNA of the blog so all phases can reference it. It is derived from analysis of the 18 existing posts (2012–2026).

- [ ] **Step 1: Create the style guide file**

```markdown
---
name: blog-style-guide
description: Style reference for Fruch's Blog — tone, structure, conventions derived from existing posts
type: reference
---

# Fruch's Blog — Style Guide

## Voice & Tone

- **Conversational and casual.** Write like you're explaining something to a friend over coffee.
- **First-person singular.** "I", not "we" (unless referring to a team).
- **Self-deprecating humor welcome.** Light jabs at yourself, your procrastination, your past code decisions.
- **Opinionated but not preachy.** State your preference, show why, move on.
- **Occasional Hebrew or slang.** A closing "יאללה" or "Fruch out..." is on-brand.

## Structure Patterns

Posts on this blog follow one of these proven structures:

1. **Problem → Solution narrative** (most common)
   - Set the scene / describe the pain point
   - Walk through the solution with code
   - Wrap up with reflections or next steps
   - Example: "ELK is Fun", "GitHub Actions"

2. **Code review / refactoring**
   - Show "before" code (someone else's or your own past code)
   - Analyze what's wrong
   - Show improved version with explanation
   - Example: "KISS - Keep it shorter short"

3. **Story-driven technical post**
   - Personal anecdote or journey (procrastination, conference, discovery)
   - Pivot to technical content with code examples
   - Close with personality (humor, call-to-action, sign-off)
   - Example: "Coodie", "Hello World"

4. **Conference / event recap**
   - Highlights and personal takeaways
   - Links to talks, slides, repos
   - Example: "EuroPython 2020", "DevOpsDayTLV"

## Front Matter Template

```yaml
---
layout: post
title: "Title — prefer punny, catchy, or playful"
description: "One-liner hook for SEO and social cards"
category: python  # or: devops, testing, databases, conferences, general
tags: [tag1, tag2, tag3]
---
```

## Formatting Conventions

- **Headings:** Use `##` for main sections. Avoid `#` in body (Jekyll uses title from front matter).
- **Code blocks:** Use fenced triple-backtick with language identifier. For older posts `{% highlight lang %}` was used — new posts should use fenced blocks.
- **Links:** Prefer reference-style links at the bottom of the post: `[text][ref]` with `[ref]: url` at the end.
- **Images:** Minimal usage. When used, full-width: `<img src="{{ site.url }}/assets/img/filename.png" width="100%" />`
- **Length:** No fixed requirement. Ranges from ~400 words (quick tips) to ~7000 words (deep dives). Let the topic dictate.
- **Emphasis:** Bold for key terms/tools on first mention. Italics for book/project names or asides.
- **Lists:** Bulleted for features/highlights. Numbered for sequential steps or ranked items.

## Things to Avoid

- Corporate/formal language ("In this blog post, we will explore...")
- Excessive emojis
- Walls of text without code or formatting breaks
- Clickbait titles that don't deliver
- Rewriting the documentation — link to it, show the interesting parts

## Sign-off Style

Posts often end with a casual closer — a call to action (star the repo, send PRs), a joke, or a short Hebrew phrase. Not every post needs one, but they add personality.
```

- [ ] **Step 2: Verify the file was created**

Run: `cat .claude/skills/blog-style-guide.md | head -5`
Expected: frontmatter with `name: blog-style-guide`

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/blog-style-guide.md
git commit -m "feat: add blog style guide for post writing skill"
```

---

### Task 2: Create the `_drafts` Directory

**Files:**
- Create: `_drafts/.gitkeep`

Jekyll supports a `_drafts/` directory for work-in-progress posts. This keeps drafts out of the published site.

- [ ] **Step 1: Create the drafts directory with a .gitkeep**

```bash
mkdir -p _drafts && touch _drafts/.gitkeep
```

- [ ] **Step 2: Verify Jekyll excludes drafts from build by default**

Jekyll natively supports `_drafts/` — posts in this directory are only shown when running `jekyll serve --drafts`. No config change needed.

- [ ] **Step 3: Commit**

```bash
git add _drafts/.gitkeep
git commit -m "feat: add _drafts directory for work-in-progress posts"
```

---

### Task 3: Build the Blog Post Writer Skill — Phase 1 (Brainstorm)

**Files:**
- Create: `.claude/skills/blog-post-writer.md`

This is the main skill file. Phase 1 handles raw topic brainstorming — the user dumps ideas, keywords, and half-formed thoughts, and the skill helps mix and refine them into candidate topics.

- [ ] **Step 1: Write the skill file with Phase 1 (brainstorm) logic**

The skill should:
- Accept raw topics, keywords, links, or half-thoughts from the user
- Cross-pollinate ideas (find intersections between topics)
- Output a ranked list of candidate blog post ideas with one-liner descriptions
- Save the brainstorm output to `_drafts/brainstorm-YYYY-MM-DD.md`
- Reference the style guide for tone alignment

```markdown
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
```

- [ ] **Step 2: Verify the skill file is syntactically correct**

Run: `head -10 .claude/skills/blog-post-writer.md`
Expected: Valid YAML front matter with `name: blog-post-writer`

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/blog-post-writer.md
git commit -m "feat: add blog-post-writer skill with brainstorm, outline, write, and picture phases"
```

---

### Task 4: Verify Skill Discovery

**Files:**
- Read: `.claude/skills/blog-post-writer.md`
- Read: `.claude/skills/blog-style-guide.md`

- [ ] **Step 1: Verify both skill files exist and have correct frontmatter**

Run: `ls -la .claude/skills/`
Expected: `blog-post-writer.md` and `blog-style-guide.md` both present

- [ ] **Step 2: Test invoking the skill**

Ask Claude Code: `/blog-post-writer brainstorm`
Expected: The skill loads and prompts the user for raw topic input

- [ ] **Step 3: Verify the _drafts directory exists**

Run: `ls -la _drafts/`
Expected: `.gitkeep` file present

---

### Task 5: Update the Modernization Plan

**Files:**
- Modify: `docs/plans/modernization-plan.md` (after Phase 4, before Summary)

- [ ] **Step 1: Add Phase 5 to the modernization plan**

Add after the Phase 4 section (line ~340) in `docs/plans/modernization-plan.md`:

```markdown
### Phase 5 – Blog Writing Workflow (ongoing)

- [ ] Extract style guide from existing posts → `.claude/skills/blog-style-guide.md`
- [ ] Create `_drafts/` directory for work-in-progress posts
- [ ] Build `blog-post-writer` Claude Code skill with four phases:
  - **Brainstorm:** Dump raw topics → AI mixes and cross-pollinates → ranked candidate list
  - **Outline:** Pick a topic → AI builds structured outline with section plan and code placeholders
  - **Write:** Guided section-by-section writing session with style enforcement
  - **Picture:** AI-generated image prompt suggestions matching post content and tone
- [ ] Validate skill works end-to-end with a test blog post
- [ ] Iterate on style guide as new posts establish patterns

> See full implementation plan: `docs/superpowers/plans/2026-03-21-blog-post-writer-skill.md`
```

- [ ] **Step 2: Commit**

```bash
git add docs/plans/modernization-plan.md
git commit -m "docs: add Phase 5 (blog writing workflow) to modernization plan"
```
