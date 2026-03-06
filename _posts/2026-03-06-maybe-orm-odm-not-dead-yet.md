---
layout: post
title: "Maybe ORM/ODM are not dead? Yet..."
description: "Benchmarking coodie against raw CQL and cqlengine reveals that the ORM tax might be far smaller than you think."
category: python
tags: [python, cassandra, scylladb, ai, open-source, pydantic, benchmarks]
---
{% include JB/setup %}

So, let's pick up where we left off. A couple of weeks ago, I wrote about how I took a 4-year-old fever dream—an ODM for Cassandra and ScyllaDB called [coodie]—and let an AI build the whole thing while I sipped my morning coffee.

It was a fun experiment. But then, a funny coincidence happened (or maybe the algorithm just has a sick sense of humor).

Right after I hit publish and started feeling good about my newfound "prompt engineer" status, I was listening to an episode of the [pythonbytes podcast] discussing Michael Kennedy's recent post, [Raw+DC: The ORM pattern of 2026?]. The overarching thesis of their discussion? ORMs and ODMs are fundamentally dead. They are a relic of the past, bloated, abstraction-heavy, and ultimately, absolute performance killers.

I actually fired off a Twitter thread in response to it. And honestly, at first, I had to concede. They make a really good point. I spend my days deep in the ScyllaDB trenches, where we fight for every single microsecond. Putting a thick Python abstraction layer on top of a highly optimized driver usually sounds like a brilliant way to turn a sports car into a tractor.

But it got me thinking. How bad was coodie? Was my AI-generated Beanie-wannabe actually a performance disaster waiting to happen?

## Giving it a test run

Like any respectable developer looking for an excuse to avoid real work, I decided to put my money where my AI-generated mouth is. Instead of sitting at my desk, I just offloaded the whole task to the Copilot agent from my phone to run some extensive benchmarks.

I didn't just want to compare coodie to existing solutions like [cqlengine]. I wanted to establish an absolute performance floor. I wanted to test it against the Raw+DC pattern (Python dataclasses + hand-written CQL with prepared statements) to see exactly how much the "ORM tax" was really costing us.

The test spun up a local ScyllaDB node, hammered it with various workloads—inserts, reads, conditional updates, batch operations—and fetched the results back.

## The finally surprising results

I had the agent run the script. I fully expected coodie to be heavily penalized. We all accept slower performance in exchange for autocomplete, declarative schemas, and not writing raw CQL strings.

I stared at the results the agent sent back to my screen. Then I told it to clear the cache, restart the Scylla container, and run it again just to be sure.

The results were genuinely surprising, and running them actually highlighted a few spots where we could squeeze out even more performance, leading straight to [PR #190] to apply those lessons learned.

Here is the breakdown of what the agent and I found across the board.

### Three-way Benchmark Results (scylla driver)

| Benchmark | Raw+DC (µs) | coodie (µs) | cqlengine (µs) | coodie vs Raw+DC | coodie vs cqlengine |
|-----------|-------------|-------------|-----------------|------------------|---------------------|
| single-insert | 456 | 485 | 615 | **1.06×** | 0.79× ✅ |
| insert-if-not-exists | 1,180 | 1,170 | 1,370 | **~1.00×** | 0.85× ✅ |
| insert-with-ttl | 448 | 469 | 640 | **1.05×** | 0.73× ✅ |
| get-by-pk | 461 | 520 | 665 | **1.13×** | 0.78× ✅ |
| filter-secondary-index | 1,370 | 2,740 | 8,530 | **2.00×** 🟠 | 0.32× ✅ |
| filter-limit | 575 | 627 | 1,220 | **1.09×** | 0.51× ✅ |
| count | 904 | 1,500 | 1,590 | **1.66×** 🟡 | 0.94× ✅ |
| partial-update | 409 | 960 | 542 | **2.35×** 🔴 | 1.77× ❌ |
| update-if-condition (LWT) | 1,140 | 1,620 | 1,340 | **1.42×** 🟡 | 1.21× ❌ |
| single-delete | 941 | 925 | 1,190 | **~1.00×** | 0.78× ✅ |
| bulk-delete | 872 | 921 | 1,200 | **1.06×** | 0.77× ✅ |
| batch-insert-10 | 596 | 634 | 1,700 | **1.06×** | 0.37× ✅ |
| batch-insert-100 | 42,800 | 1,960 | 52,900 | **0.05× 🚀** | 0.04× ✅ |
| collection-write | 448 | 485 | 679 | **1.08×** | 0.71× ✅ |
| collection-read | 478 | 508 | 689 | **1.06×** | 0.74× ✅ |
| collection-roundtrip | 939 | 1,060 | 1,380 | **1.13×** | 0.77× ✅ |
| model-instantiation | 0.671 | 2.02 | 12.1 | **3.01×** 🔴 | 0.17× ✅ |
| model-serialization | 10.1 | 2.05 | 4.56 | **0.20× 🚀** | 0.45× ✅ |

## Summary of Findings

**Near Parity on the Hot Paths:** For standard reads (get-by-pk), inserts, deletes, and basic limited queries, coodie is operating with a completely negligible overhead compared to writing raw CQL by hand (usually hovering around 5-13% tax). It also outperforms cqlengine across the board on these operations.

**Pydantic V2 is a beast:** We need to remember that Pydantic V2 is basically a blazing-fast Rust engine wearing a Python trench coat. The data validation, object instantiation, and serialization happen at the speed of Rust, keeping the overhead minimal from the start. Just look at the serialization and batch performance multipliers!

**The AI kept it lean:** The code the LLM generated wasn't building massive ASTs or doing unnecessary query translations. coodie essentially formats a clean dictionary and hands it straight to the underlying Scylla driver to do its native magic. It gets out of the way.

**Lessons Learned ([PR #190]):** Even with great initial numbers, running the full benchmark suite revealed bottlenecks on things like partial-update and count. We realized we were doing redundant data validation during read operations when fetching data we already knew was valid straight from the database. By bypassing the extra validation pass and loading the raw rows more directly into the Pydantic models (using `model_construct()` for DB data), we can shave off the remaining overhead.

## Wrapping up

So, maybe ORM/ODM are not dead? Yet...

If the final overhead of using an ODM on hot paths is a measly 5-13%, but in exchange I get full type-safety, declarative schemas, and zero boilerplate, I am taking the ODM every single time.

It seems my digital sidekick built something that is actually production-ready, and with a little bit of human-driven optimization, it screams.

You can check out the code, star it, or run your own tests over at [github.com/fruch/coodie].

PRs are welcome. יאללה, let's see how fast we can make it.

[coodie]: https://github.com/fruch/coodie
[pythonbytes podcast]: https://pythonbytes.fm
[Raw+DC: The ORM pattern of 2026?]: https://blog.michaelckennedy.net
[cqlengine]: https://docs.datastax.com/en/developer/python-driver/latest/cqlengine/
[PR #190]: https://github.com/fruch/coodie/pull/190
[github.com/fruch/coodie]: https://github.com/fruch/coodie
