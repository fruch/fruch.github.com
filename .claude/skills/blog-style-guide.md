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

## Sounding Like Me, Not Like a Model

I only publish posts I wrote myself. Readers, news feeds and AI detectors call out AI-written posts, and Pangram, GPTZero and Copyleaks all scored an AI-drafted version of the coodie post at 96-100% AI. These are the habits that gave it away.

**My numbers.** `_tools/voice_check.py` measures them on my posts from before ChatGPT (2012-2022):

| Habit | My old posts | AI-drafted coodie post |
|---|---|---|
| I / my / me / we, per 1000 words | ~47 | ~10 |
| Mean sentence length | ~27 words | ~22 words |
| Lists of three ("a, b and c"), semicolons, mid-sentence colons | almost none | 3-4 of each per 1000 words |

So I write long sentences of uneven length, mostly about what *I* did, tried or broke. Models write shorter, even sentences about what *the thing* does.

**Tells to cut.** Each example is a real sentence the detectors flagged in an AI draft:

- Staged openers: "Honestly, …", "Of course, …", "In practice, …", "Here's the thing". Start with the point.
- Punchline closers: "No pressure.", "I'll take that.", "One file, not 47 models." The paragraph already made the point.
- Sayings: "cqlengine gives you `sync_table()` and wishes you luck", "…and it shows", "you're paying for async without getting much back". Say the plain fact.
- X-not-Y contrasts and either/or setups: "not just X but Y", "either stalls the loop or goes to a thread pool, and in both cases…".
- Colon reveals: "It's the same trick ScyllaDB uses on itself: …"
- Lists of three by reflex, and neat pairs like "hide a real regression (or invent a fake one)".
- Stock AI words: delve, pivotal, crucial, robust, seamless, showcase, underscore, testament, landscape.
- Em dashes as the default connector.

**What doesn't help.** I tested the vendored `/humanizer` and `/stop-slop` skills by having them rewrite the coodie post. They removed the phrases above, but the sentences came out *shorter and more even*, which is further from my voice, and first person barely moved. Rewriting with a "humanizer" only hides that a post is AI-written. Use these tools to find problems, and fix them in my own words.

## Checking a Draft

From most to least useful:

1. **`python3 _tools/voice_check.py _drafts/<post>.md`.** It compares the draft with my pre-2022 posts and lists the lines with the tells above. It runs locally with the stdlib only.
2. **`/stop-slop` and `/humanizer`, as checklists only.** Ask "list the tells in this paragraph", never "rewrite this".
3. **Free web detectors: [GPTZero](https://gptzero.me) and [Pangram](https://www.pangram.com).** They highlight sentences and are the ones that caught the AI draft. Pangram's free checks are limited per day, so run it last, on the final draft.
4. **Skip the local Hugging Face detectors** (tabularisai, desklib, the RoBERTa detectors). They scored the 96%-AI draft about 0% AI.

## Sign-off Style

Posts often end with a casual closer — a call to action (star the repo, send PRs), a joke, or a short Hebrew phrase. Not every post needs one, but they add personality.
