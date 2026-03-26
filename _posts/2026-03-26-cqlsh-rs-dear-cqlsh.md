---
layout: post
title: "Dear cqlsh: dependencies was killing us. p.s. we rewrote you in rust."
description: "How I rebuilt the Cassandra CQL shell in Rust with Claude as co-pilot, co-author, and occasional clippy enforcer - and what I learned about AI-assisted development the second time around."
category: rust
tags: [rust, cassandra, scylladb, ai, claude, open-source, cqlsh]
---
{% include JB/setup %}

<link href="https://fonts.googleapis.com/css2?family=Patrick+Hand&display=swap" rel="stylesheet">
<div style="background-color: #fdf6e3; border: 1px solid #d4b896; border-radius: 4px; padding: 1.5em 2em; margin-bottom: 2em; font-family: 'Patrick Hand', cursive; font-size: 1.3em; font-weight: 700; line-height: 1.9; color: #2b1f0e; box-shadow: 2px 2px 6px rgba(0,0,0,0.15);">

<p>Dear cqlsh,</p>

<p>I vouched for you. I told the team you were fine. I forked you, catered to you, vendored your dependencies and your dependencies' dependencies. I patched things upstream I knew would never merge. I pinned your Python, re-pinned it after the OS upgraded, and explained to people - with a straight face - why that was totally normal and not a problem at all.</p>

<p>I wrote you twice already. You never wrote back.</p>

<p>I'm not even mad. I get it - you're busy. 30+ CLI flags. 25 CQL types. A COPY engine with enough options to fill a man page. You've got a lot going on.</p>

<p>But I found someone faster. They compile to a static binary. No runtime. No vendoring. No "which Python are we using today." They just... work.</p>

<p>I hope you understand.</p>

<p>Yours (for now),<br/>Israel</p>

</div>

---

This is the story of [cqlsh-rs] - a ground-up Rust rewrite of the Python `cqlsh`, the interactive CQL shell used daily by everyone working with Cassandra and ScyllaDB. It's also a story about what happens when you take the lessons from one AI-assisted project and apply them to another project.

## Why bother rewriting? because packaging is a nightmare.

ScyllaDB ships a **relocatable package** - a self-contained bundle with its own Python runtime baked in. The idea is clever: the system Python can change, upgrade, or disappear entirely, and ScyllaDB's startup scripts and `cqlsh` keep working because they're running against a known, pinned Python version inside the bundle.

Except `cqlsh` has to live inside that bundle.

And `cqlsh` is a Python tool. With dependencies. Which have dependencies. Which all need to be vendored in alongside the bundled Python. Every time cqlsh or one of its deps needs updating - a bug fix, a new Cassandra protocol version, a security patch - you're not just updating a package. You're updating the bundle. Testing the bundle. Shipping the bundle. And if something conflicts or breaks inside that carefully pinned environment, it's your problem to untangle.

A static Rust binary sidesteps all of this. You compile once per target, you get a single file with zero runtime dependencies, and you ship it. Done.

The second pain point is **COPY TO/FROM** - cqlsh's built-in feature for bulk-exporting and importing table data to CSV. It's one of the most-used features, and it's been carrying around a long list of bugs for years. It does have parallel workers - threads and processes - but the machinery is complicated, fragile, and notoriously hard to test. The bug list reflects that.

Both of these are solvable in Rust. So, the question became: is now the time to actually solve them?

## It all started with a BIG plan (in the melody of The Big Bang Theory)

In my [previous post][coodie-post] I wrote about using GitHub Copilot to bring a 4-year-old Python idea - [coodie], a Pydantic ODM for Cassandra - back to life. That project was relatively contained: give the AI a concept, come back to a working implementation. Fire and forget, more or less.

cqlsh-rs is a different category of project. The original Python cqlsh has been around for over a decade. It has hundreds of CLI flags, a compatibility matrix that spans multiple database versions, a COPY engine with 30+ options per direction, tab completion that has to be schema-aware, and a type system covering 25+ CQL types with specific formatting rules. Shipping something that "mostly works" is not good enough if people are going to actually switch to it - every muscle-memory command has to work the same way.

So before writing a single line of Rust, I started with a plan.

That plan started as one document. Then it grew. Then it became a master design document plus sub-plans. By the time the architecture settled, there were **19 sub-plans** (SP01 through SP19) covering everything from the CLI argument parser to the CQL type formatter to the COPY engine to a future `--ai-help` flag for offline CQL error diagnostics.

Here's what the roadmap looked like near the start:

<img src="{{ site.url }}/assets/img/cqlsh-rs-roadmap-early.svg" width="100%" alt="cqlsh-rs development roadmap early state: 5/108 tasks, 5% complete, ETA Dec 2026" />

5 out of 108 tasks. 0.4 tasks per day. The footer on that SVG read: *"Approximately 8.9 months remaining... just like Windows said."*

Reader, it did not take 8.9 months.

## from cozy browser tab to "wait, why is there a skill for that?"

I started in Claude web. Not because that's my comfort zone - with Copilot I liked the browser because it made the conversation visible to the team, a kind of shared thinking space. Same instinct here. Design conversations, architecture decisions, trade-off explorations - all of it happened in the browser before a single file was created. What driver to use. How to structure the CLI argument parsing. Whether to write a hand-rolled CQL parser or keep it simple with a line-buffer approach. The kind of questions that are genuinely better answered in conversation than in code.

The master plan came together there. So did the first sub-plans, and the initial CI skeleton.

Then I started exploring Claude Code - the CLI - and somewhere around phase 2, the browser tab closed and didn't reopen.

The difference is hard to pin down to one thing. It's partly the feedback loop: you're in the same environment as the code, so `cargo test` runs immediately after a change, failures surface in context, and the next prompt can reference the actual output. And it's partly just familiarity - the more you use it, the more you learn to point it at exactly the right problem.

The transition wasn't planned. It just happened because the tool kept proving useful in situations I hadn't expected.

### skills: write your conventions once, use them forever

The other piece that made this work at scale is the **skills library** - a directory of reusable instruction files, each focused on one kind of task. Instead of re-explaining how tests should be structured in every prompt, you write it once:

- `/rust-testing` - what to test at the unit layer vs. the integration layer, how to use `assert_cmd` for CLI tests, when to reach for `insta` snapshots
- `/rust-clippy` - run Clippy with strict settings and fix everything it complains about
- `/rust-error-handling` - idiomatic error handling patterns for this codebase
- `/development-process` - the full loop: review the relevant sub-plan, design tests first, implement, run tests, update the plan, commit

I carried the pattern directly from coodie. The specific skills are different - Python vs. Rust - but the idea is the same. It compounds. Each skill you write makes every subsequent feature cheaper to build.

### living documents, or: an outdated plan is worse than no plan

The 19 sub-plans are not static specs. They're living documents - updated when decisions are made, not written upfront and then abandoned. When a design decision changes mid-implementation, the plan changes too. When a task is done, the checkbox gets ticked. When a new edge case surfaces, it gets added.

This matters more than it sounds. An outdated plan is worse than no plan, because the AI will follow it faithfully - in the wrong direction.


## what's in the box

Rust with Tokio for async. The [scylla] crate for the database driver. [rustyline] for the REPL and line editing. [comfy-table] and [owo-colors] for output formatting. [testcontainers-rs] for spinning up real Cassandra instances in CI.

Nothing exotic. The interesting part isn't the stack - it's what it takes to get every CQL type to format exactly like the Python implementation, right down to float precision and frozen collection syntax. That's where most of the compatibility work lives.

## how far down the rabbit hole did we go

Here's the same roadmap today:

<img src="{{ site.url }}/assets/img/cqlsh-rs-roadmap-current.svg" width="100%" alt="cqlsh-rs development roadmap current state: 64/108 tasks, 59% complete" />

Phases 1 through 3 are done. The shell works: you can connect, run queries, get formatted output with colors and pagination, tab-complete keyspace and table names, run DESCRIBE on anything, and use SOURCE to execute a file. Phase 4 - COPY TO/FROM - is implemented. Phase 5 (testing) is in progress, with 327 tests and counting.

The plan didn't slow things down - having a plan is what made the acceleration possible.

## takeaways (free as in free beer)

**Planning pays, but living documents is a nice touch.** A static plan written at the start and never touched again is a liability. A plan that gets updated as decisions are made is an asset - and the primary reason Claude can work effectively across multiple sessions on a project this size.

**Skills compound.** Half the work is finding the right skill for the task and adapting it to the project - the conventions, the patterns, the "this is how we do it here." Once that's written down, every feature after it gets cheaper. You're not re-explaining, you're reusing.

**The workflow is never done.** The pace of this space is genuinely disorienting. Tools that didn't exist six months ago are now part of the daily loop. What worked last month might not be the best approach today. By the time you've figured out a solid workflow, something new has shipped and you're reconsidering it again. That's not a complaint - it's just the reality. You update as you go.

**It's still writing code - just different.** (I have a bit of trouble with the word "engineering" - no diploma here.) Claude doesn't replace judgment on architecture, on what actually matters to users, on "is this the right trade-off." It removes the friction between having a clear idea of what you want and that thing existing. Whether that makes it better or worse probably depends on the day.

**Lessons from one project carry straight into the next.** The skills pattern from coodie? Carried into cqlsh-rs with a different language and a different domain. You don't start from zero - you start from what you already learned, and the AI follows the same process docs you wrote last time.

## things to look forward to

One idea that popped up during this: a `--ai-help` flag that embeds a small local model to give offline diagnostics when your CQL query fails. Building an AI-assisted tool with an AI assistant, which will assist with AI-assisted queries. I'm going to stop thinking about that too hard.

For the model routing we'll probably use LiteLLM - heard it's become quite popular lately.

<img src="{{ site.url }}/assets/img/cqlsh-rs-stan-desk.png" width="100%" alt="A cluttered obsessive fan's desk with sticky notes, stack traces, and a glowing purple laptop in the corner" />

I had fun. Claude had fun too, probably. I didn't ask.

[cqlsh-rs]: https://github.com/fruch/cqlsh-rs
[fruch/cqlsh-rs]: https://github.com/fruch/cqlsh-rs
[coodie]: https://github.com/fruch/coodie
[coodie-post]: https://fruch.github.io/python/2026/02/24/coodie-ai-pydantic-odm
[scylla]: https://github.com/scylladb/scylla-rust-driver
[rustyline]: https://github.com/kkawakam/rustyline
[comfy-table]: https://github.com/nukesor/comfy-table
[owo-colors]: https://github.com/jam1garner/owo-colors
[testcontainers-rs]: https://github.com/testcontainers/testcontainers-rs
