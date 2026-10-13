---
layout: post
title: "coodie gets a day job"
description: "Why Argus, ScyllaDB's test tracking system, moved 47 models from cqlengine to coodie, and what async, pluggable drivers and Pydantic types bought it."
category: python
tags: [python, cassandra, scylladb, open-source, pydantic, asyncio, fastapi, argus]
status: draft
---
{% include JB/setup %}

<img src="{{ site.baseurl }}/assets/img/coodie-day-job.jpg" width="75%" style="float: none; display: block; margin: 0 auto 1.5em;" alt="The coodie mascot, a knitted beanie wearing an ARGUS badge and holding a coffee, standing at a desk with a dashboard of green checkmarks" />

Up until now, [coodie] was nice pet project, my first greenfield AI aided project with [fun origin story][post1]. now it's getting "real" day job, as we about to announce it replacing cqlengine cause it proven it self in the first field project.
lets jump right into explaining the how and why:

Now it has a day job, and not an easy one: it holds the test results ScyllaDB QA looks at before every release. No pressure.

## Argus, and five years of cqlengine

[Argus] is our test tracking system. [SCT] longevity runs, dtests and the driver matrix jobs all report into it (runs, events, packages, results tables, Jira and GitHub issues, release plans), and it's one of the places QA goes to decide if a ScyllaDB release is ready to ship.

It has been on **cqlengine**, the object mapper that comes inside the Python driver, since its very first commit back in November 2021. Five years later that added up to 47 models and 18 user-defined types, all sync, sitting behind Flask. And in 35 places cqlengine just wasn't enough, so the code went down to hand-written prepared statements, like this one:

```python
cluster = ScyllaCluster.get()
query = cluster.prepare("SELECT build_id, start_time, release_id, group_id, assignee, "
                        f"test_id, id, status, investigation_status, build_job_url, build_number, scylla_version FROM {cls.table_name()} WHERE assignee = ?")
rows = cluster.session.execute(query=query, parameters=(user_id,))
```

When [Alexey Kartashov][k0machi], who maintains Argus, started moving the backend from Flask to FastAPI, he hit cqlengine's limits pretty quickly. There's no asyncio API, it only knows one driver, and the models carry no type information at all. Which, conveniently, is the exact list of things I built coodie for.

## Async, this time for real

<img src="{{ site.baseurl }}/assets/img/coodie-async.jpg" width="60%" style="float: none; display: block; margin: 0 auto 1.5em;" alt="The coodie mascot juggling five glowing SELECT bubbles at once, while a dusty cqlengine filing cabinet hands out one paper at a time to a bored queue under a clock" />

A blocking mapper inside a FastAPI app means each query either stalls the event loop or gets shipped off to a thread pool, and in both cases you're paying for async without getting much back.

coodie has two APIs over the same models, `coodie.sync` for blocking code and `coodie.aio` for asyncio. The field annotations and query builder are shared, only the `Document` base class is different, and that's what let Argus do it in two steps. First [argus#1058][pr1058] moved every model to the sync API, one commit per service. Then [argus#1106][pr1106] flipped the models to `coodie.aio` and turned every route, auth dependency and service method that talks to ScyllaDB into a coroutine.

In practice, for a request that needs two lookups that don't depend on each other, it looks like this:

```python
# before: cqlengine, sync, one query after the other
owned_plans = list(ArgusReleasePlan.find(owner=user.id).allow_filtering().all())
participating_plans = list(ArgusReleasePlan.find(participants__contains=user.id).allow_filtering().all())

# after: coodie.aio, both queries in flight at once
owned_plans, participating_plans = await asyncio.gather(
    ArgusReleasePlan.find(owner=user.id).allow_filtering().all(),
    ArgusReleasePlan.find(participants__contains=user.id).allow_filtering().all(),
)
```

<img src="{{ site.baseurl }}/assets/img/coodie-sequential-vs-gather.svg" width="70%" style="float: none; display: block; margin: 0 auto 1.5em;" alt="Timeline: before, two queries run one after the other; after, both run at the same time and the request finishes when the slower one returns" />

Speed was the whole reason for doing this. Alexey went hotspot by hotspot, one `perf` commit per endpoint, and each commit message says which serial round-trips it got rid of.

So I went digging in the Argus Grafana for numbers. Prometheus there only keeps data from the end of August, which means my "before" is already sync coodie on Flask and uWSGI (the cqlengine days are gone from the metrics, sadly). Still, two steps show up clearly:

<img src="{{ site.baseurl }}/assets/img/argus-latency-daily.svg" width="90%" style="float: none; display: block; margin: 0 auto 1.5em;" alt="Daily request latency in Argus production. Before the FastAPI switch p99 is around 1.5 seconds and p95 around 450 ms; after it p99 drops below 250 ms and p95 to about 70 ms. After the coodie.aio switch p99 settles under 100 ms." />

The FastAPI move, with coodie still sync, took care of the tail. p99 across all endpoints went from about 1.5 s to under 250 ms and p95 from about 450 ms to about 70 ms, while the median didn't move at all (about 32 ms). Fast requests were always fast; the slow ones just stopped waiting in line behind each other.

The `coodie.aio` switch is easier to see per endpoint, on the ones where the `gather` trick applied:

<img src="{{ site.baseurl }}/assets/img/argus-latency-endpoints.svg" width="90%" style="float: none; display: block; margin: 0 auto 1.5em;" alt="Mean latency per endpoint across three phases. submit_run_config: 1621, 1139, 304 ms. get_testrun: 53, 32, 19 ms. submit_pytest_result: 140, 50, 50 ms. get_pytest_test_field_stats: 106, 53, 46 ms. submit_results: 247, 111, 117 ms." />

`submit_run_config` dropped from 1.1 s to 0.3 s and `get_testrun` from 32 ms to 19 ms. `submit_pytest_result`, the busiest endpoint by far (about 2 million calls in two weeks), didn't change, and it shouldn't: it's a single write, nothing to run in parallel. Since the async switch, p99 sits under 100 ms on most days.

Of course, running queries side by side only pays off if each one is cheap. If the mapper puts a heavy tax on every call, `gather` just gives you the slow calls in parallel. My [previous post][post2] measured that tax against hand-written CQL and cqlengine, and it came out small.

Since then the benchmarks run in CI on every PR, against both the scylla and acsylla drivers. If a PR makes coodie slower it gets a comment, and every run lands on a [benchmark history dashboard][bench], so a regression looks like a step in a chart. Except CI runners are noisy, and noise can hide a real regression (or invent a fake one), so next I'm [counting CPU instructions][pr323] for the in-memory benchmarks, which the runner hardware can't mess with.

Performance  work is a never-ending story, hence I've put lots of focus to having those automated on the PR level, and tracked and outperform cqlengine that didn't had this kind of attention for years (maybe ever)

The same PR also got rid of most of the hand-written CQL. The prepared statement from before becomes a query-builder call with a column projection:

```python
# after: no CQL string, no table name interpolation, and it's async
async def get_jobs_assigned_to_user(cls, user_id: UUID) -> list[dict]:
    return await select_rows(
        cls.find(assignee=user_id),
        "build_id", "start_time", "release_id", "group_id", "assignee", "test_id",
        "id", "status", "investigation_status", "build_job_url", "build_number", "scylla_version",
    )
```

`select_rows` is a two-line Argus helper on top of coodie's `.only(...).values_list(...)`. Out of the 35 raw CQL sites, what's left are the statements the query builder can't express yet. While writing this post I found one of them, a [`WRITETIME` projection][issue330], and opened an issue for it.

## Pluggable drivers

<img src="{{ site.baseurl }}/assets/img/coodie-drivers.jpg" width="60%" style="float: none; display: block; margin: 0 auto 1.5em;" alt="The coodie mascot plugging four plugs labeled scylla, cassandra, acsylla and rust into a power strip" />

cqlengine lives inside the DataStax-derived driver and can't use anything else. coodie sits on a small driver interface instead, and today there are four backends behind it:

- **scylla-driver** (`driver_type="scylla"`, the default): shard-aware, and the one I'd pick for ScyllaDB.
- **cassandra-driver** (`"cassandra"`): the upstream DataStax driver.
- **[acsylla]** (`"acsylla"`): async-native, Cython bindings over the C++ driver.
- **[scylladb-rs-driver]** (`"python-rs"`): async-native, the Rust driver exposed through PyO3. Still experimental.

Switching is one argument, models and queries stay as they are, and the async-native ones work from the sync API too, through a sync bridge:

```python
from coodie.aio import init_coodie

await init_coodie(hosts=["node1", "node2"], keyspace="argus", driver_type="acsylla")
```

Argus used the pluggable part in a way I didn't plan for. It already had a tuned connection (authentication, a whitelist load-balancing policy, `QUORUM` execution profiles), and opening a second one made no sense, so Alexey subclassed coodie's driver around the existing session and registered it as the default (trimmed):

```python
class ArgusCoodieDriver(CassandraDriver):
    def _wrap_future(self, driver_future) -> asyncio.Future:
        return await_all_pages(driver_future)

self.coodie_driver = ArgusCoodieDriver(
    session=connection.get_session(connection="default"),
    default_keyspace=self.config["SCYLLA_KEYSPACE_NAME"],
)
register_driver("default", self.coodie_driver, default=True)
```

That's what made the gradual migration possible, since cqlengine and coodie shared one session while services moved over one by one. (It also turned up a [bug in how coodie handles sessions with execution profiles][issue329], which I found while writing this, so thanks, Argus.) And it leaves one place to swap drivers later; the migration PR calls `db.py` "the seam for the future acsylla driver swap". One file, not 47 models.

## Pydantic types

<img src="{{ site.baseurl }}/assets/img/coodie-moving-day.jpg" width="60%" style="float: none; display: block; margin: 0 auto 1.5em;" alt="The coodie mascot carrying a box labeled MODELS from a dusty cqlengine filing cabinet to a modern server rack" />

cqlengine is older than type hints, and it shows. This is the Argus `User` model before the migration:

```python
class User(Model):
    id = columns.UUID(primary_key=True, default=uuid4)
    username = columns.Text(index=True)
    full_name = columns.Text()
    password = columns.Text()
    email = columns.Text(index=True)
    registration_date = columns.DateTime()
    roles = columns.List(value_type=columns.Text)
    picture_id = columns.UUID(default=None)
    service_user = columns.Boolean(default=lambda: False)
```

Ask your type checker what `user.roles` is and it has no idea. Same model in coodie:

```python
class User(Document):
    id: Annotated[UUID, PrimaryKey()] = Field(default_factory=uuid4)
    username: Annotated[str, Indexed()]
    full_name: Optional[str] = None
    password: str
    email: Annotated[Optional[str], Indexed()] = None
    registration_date: datetime
    roles: list[str] = Field(default_factory=list)
    picture_id: Optional[UUID] = None
    service_user: Optional[bool] = False

    class Settings:
        name = "user"
```

It's a plain **Pydantic v2** model, with `Annotated` markers for keys and indexes. Your editor and mypy know every field's type (coodie ships `py.typed`), bad data gets rejected when the object is built instead of when some other service reads it a week later, and `model_dump()` hands the API layer a dict, so FastAPI can use the same class as its response model.

The types also made a cleanup worth the effort. In [argus#1066][pr1066], key columns and always-populated fields went from `Optional[...]` to required, in the places where the service always writes them and the data had no NULLs. cqlengine has `required=True` too, but it's only checked at runtime. In coodie, `str` vs `Optional[str]` is what both Pydantic and the type checker see, so making a field required points at every caller that might pass `None` before anything runs.

## Bonus: schema migrations

cqlengine gives you `sync_table()` and wishes you luck. coodie has a real schema toolkit on top of it.

`sync_table(dry_run=True)` returns the CQL it would run, without running it. Argus used that to check every model against the live cluster, with table, type and index names pinned to what cqlengine had created (legacy names like `packageversion_v2` included), and an empty result meant no data migration. coodie also warns you about schema drift, when the database has columns the model doesn't know about. And for changes `sync_table()` shouldn't guess at, there are versioned migration files and a CLI to generate, apply, preview and roll them back:

```bash
coodie schema-diff --keyspace argus --module app.models        # what changed?
coodie makemigration --name add_rating --keyspace argus --module app.models
coodie migrate --keyspace argus --dry-run                      # preview the CQL
coodie migrate --keyspace argus                                # apply
```

Changing a field's type is where people usually get burned. `makemigration` won't emit an `ALTER` for it, it flags it as unsafe, and you do it properly in the migration file: add a new column, backfill it with `ctx.scan_table()` (token-range paging, resumable and throttled), then drop the old one. Runs take a lightweight-transaction lock so two app instances can't migrate at the same time, and wait for schema agreement before each DDL statement. Argus didn't need any of it, since it kept its schema as is, but the next schema change there has a safer path than a hand-written `ALTER TABLE`. The [schema management guide][schema] has the details.

## What production found

Honestly, less than I expected. The migration turned up exactly [one coodie issue][issue271], and everything else ran on coodie as released. But a production user and a careful code review catch different kinds of bugs, so I also ran a [full architecture review][review] afterwards, and its findings are fixed in the [1.7.x releases][release].

<!-- TODO(fruch): PLACEHOLDER written in Alexey's style from his PR comments
     (argus#1058, #1059, #1066, #1106). Every claim is from those PRs, but he
     hasn't approved it. Replace with his own words before publishing.
     Every AI detector flagged this quote as AI-written: his real words fix that. -->

> Honestly, I expected the migration to be the scary part. It wasn't - 37 core models, the plugin models and all 18 UDTs moved over one service at a time, and the schema check came back matching cqlengine's table for table (sans one vector index name, which we fixed). Zero data migration. I'll take that.
>
> The fun started after. FastAPI alone got us out of the 1.5 second p99 swamp, but we were still sitting on sync calls, and they were piling up. Flipping the models to `coodie.aio` and throwing the independent reads into `asyncio.gather` is what got us the rest of the way - p99 is now under 100 ms most days, and `submit_run_config` went from over a second to 300 ms. Same database, same schema, just not waiting on things one at a time anymore.
>
> Also, having actual types on the models means the IDE yells at me before production does. Wayy better than finding out from a stack trace.
>
> — Alexey Kartashov, Argus maintainer

## Give coodie a try

<img src="{{ site.baseurl }}/assets/img/coodie-scylladb-family.jpg" width="60%" style="float: none; display: block; margin: 0 auto 1.5em;" alt="A knitted one-eyed ScyllaDB sea monster wearing the coodie beanie and an ARGUS badge, holding a coffee next to a whiteboard mapping DB models to tables and schema" />

Argus now runs on coodie, fully async, on the same schema it had under cqlengine. A big thanks to Alexey for being the first one brave enough to put it in production, and for doing the migration so cleanly that it's now our reference example.

coodie lives in the [ScyllaDB GitHub organization][coodie], next to the drivers it builds on. cqlengine, meanwhile, is in maintenance mode: bug fixes, no new features. Starting with the next ScyllaDB Python driver release, importing cqlengine raises a deprecation warning that points to coodie (I sent that one in myself, [python-driver#1127][pd1127]).

If you’re using Scylla from python and like type annotation (i.e. pydantic and package using the same approach), you might want to give coodie a try.
If you are using cqlengine you should definitely pick it up, the [migration guide][migration] and it match [skill][migration-skill] are good places to start understanding how to get it running.
[issues] and [pull requests][pulls] are highly welcomed

[coodie]: https://github.com/scylladb/coodie
[Argus]: https://github.com/scylladb/argus
[SCT]: https://github.com/scylladb/scylla-cluster-tests
[cqlengine]: https://python-driver.docs.scylladb.com/stable/object-mapper.html
[post1]: {% post_url 2026-02-24-coodie-ai-pydantic-odm %}
[post2]: {% post_url 2026-03-06-maybe-orm-odm-not-dead-yet %}
[k0machi]: https://github.com/k0machi
[pr1058]: https://github.com/scylladb/argus/pull/1058
[pr1066]: https://github.com/scylladb/argus/pull/1066
[pr1106]: https://github.com/scylladb/argus/pull/1106
[pd1127]: https://github.com/scylladb/python-driver/pull/1127
[migration]: https://scylladb.github.io/coodie/migration/from-cqlengine.html
[argus-example]: https://scylladb.github.io/coodie/migration/argus-example.html
[issues]: https://github.com/scylladb/coodie/issues
[pulls]: https://github.com/scylladb/coodie/pulls
[migration-skill]: https://github.com/scylladb/coodie/tree/master/.github/skills/cqlengine-migration
[schema]: https://scylladb.github.io/coodie/guide/schema-management.html
[bench]: https://scylladb.github.io/coodie/benchmarks/
[pr323]: https://github.com/scylladb/coodie/pull/323
[acsylla]: https://github.com/acsylla/acsylla
[scylladb-rs-driver]: https://github.com/scylladb-zpp-2025-python-rs-driver/python-rs-driver
[issue329]: https://github.com/scylladb/coodie/issues/329
[issue330]: https://github.com/scylladb/coodie/issues/330
[issue271]: https://github.com/scylladb/coodie/issues/271
[review]: https://github.com/scylladb/coodie/blob/master/docs/reviews/2026-10-architecture-review.md
[release]: https://github.com/scylladb/coodie/releases
