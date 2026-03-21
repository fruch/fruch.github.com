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
