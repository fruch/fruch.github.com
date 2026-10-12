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

For most of its life, if you asked what [coodie] did for a living, the honest answer was "it's between jobs". It had a polished README, a [benchmark page][post2], a portfolio of demo apps, and a [great origin story][post1]. What it didn't have was a single production system willing to put it on the payroll.

As of this summer it has a day job: it holds the test results ScyllaDB QA looks at before every release. No pressure.

## Argus and five years of cqlengine

[Argus] is ScyllaDB's test tracking system. [SCT] longevity runs, dtests and driver matrix jobs all report into it: runs, events, packages, results tables, Jira and GitHub issues, release plans. It's one of the tools QA uses to decide whether a ScyllaDB release is ready.

Argus has been on **cqlengine**, the object mapper that ships inside the Python driver, since its first commit in November 2021. Five years later that meant 47 models and 18 user-defined types, all sync, all behind a Flask backend. It also meant 35 places where cqlengine wasn't enough and the code dropped down to hand-written prepared statements, like this one:

```python
cluster = ScyllaCluster.get()
query = cluster.prepare("SELECT build_id, start_time, release_id, group_id, assignee, "
                        f"test_id, id, status, investigation_status, build_job_url, build_number, scylla_version FROM {cls.table_name()} WHERE assignee = ?")
rows = cluster.session.execute(query=query, parameters=(user_id,))
```

When [Alexey Kartashov][k0machi], the Argus maintainer, started moving the backend from Flask to FastAPI, cqlengine fell short in three places:

1. It has no asyncio API.
2. It's tied to a single driver.
3. Its models carry no type information.

Those three gaps are exactly what coodie was built to close.


## 1. Async, this time for real

<img src="{{ site.baseurl }}/assets/img/coodie-async.jpg" width="60%" style="float: none; display: block; margin: 0 auto 1.5em;" alt="The coodie mascot juggling five glowing SELECT bubbles at once, while a dusty cqlengine filing cabinet hands out one paper at a time to a bored queue under a clock" />

In a FastAPI application, a blocking mapper means every query either stalls the event loop or gets pushed to a thread pool. Either way, you lose most of what async was supposed to give you.

coodie has two APIs over the same models: `coodie.sync` for blocking code and `coodie.aio` for asyncio. Field annotations and the query builder are shared; only the `Document` base class changes. That let Argus migrate in two steps:

- [argus#1058][pr1058] moved every model to coodie's sync API, one commit per service.
- [argus#1106][pr1106] switched the models to `coodie.aio` and made every route, auth dependency and service method that touches ScyllaDB a coroutine.

Here's what that changed in practice, in a request that needs two independent lookups:

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

Performance was the point of the whole exercise, not a side effect. The PR applies this pattern hotspot by hotspot, with one `perf` commit per endpoint, and each commit message records which serial round-trips it removed.

Argus production metrics show the result in two steps. Prometheus only keeps data from the end of August, so the starting point is Argus already on sync coodie, still on Flask and uWSGI.

<img src="{{ site.baseurl }}/assets/img/argus-latency-daily.svg" width="90%" style="float: none; display: block; margin: 0 auto 1.5em;" alt="Daily request latency in Argus production. Before the FastAPI switch p99 is around 1.5 seconds and p95 around 450 ms; after it p99 drops below 250 ms and p95 to about 70 ms. After the coodie.aio switch p99 settles under 100 ms." />

The move to FastAPI, with coodie still sync, fixed the tail. Across all endpoints, p99 dropped from about 1.5 s to under 250 ms, and p95 from about 450 ms to about 70 ms. The median stayed at about 32 ms: fast requests were always fast, but slow ones no longer queued behind each other.

The switch to `coodie.aio` shows up per endpoint, wherever the `gather` pattern applied:

<img src="{{ site.baseurl }}/assets/img/argus-latency-endpoints.svg" width="90%" style="float: none; display: block; margin: 0 auto 1.5em;" alt="Mean latency per endpoint across three phases. submit_run_config: 1621, 1139, 304 ms. get_testrun: 53, 32, 19 ms. submit_pytest_result: 140, 50, 50 ms. get_pytest_test_field_stats: 106, 53, 46 ms. submit_results: 247, 111, 117 ms." />

`submit_run_config` went from 1.1 s to 0.3 s, and `get_testrun` from 32 ms to 19 ms. `submit_pytest_result`, the busiest endpoint at about 2 million calls in two weeks, stayed flat: it does one write, so there was nothing to run in parallel. Since the async switch, daily p99 has settled under 100 ms most days.

Running queries in parallel only helps if each query is cheap to begin with. If the mapper adds a heavy tax to every call, `gather` just runs the slow calls side by side.

My [previous post][post2] measured that tax, benchmarking coodie against hand-written CQL and cqlengine. The answer was: small.

Since then, the benchmarks run in CI on every pull request, against both the scylla and acsylla drivers. A PR that makes coodie slower gets a comment, and the results go to a [benchmark history dashboard][bench], so a regression shows up as a step in a chart.

CI runners are noisy, though, and that noise can hide a real regression or flag a fake one. The next step is to [count CPU instructions][pr323] for the in-memory benchmarks, a number the runner hardware can't distort.

Performance work is never done. There's always another hotspot, another driver, another round of measurements. The goal is to make sure each improvement stays improved.

The same PR also retired most of the hand-written CQL. The prepared statement from earlier becomes a query-builder call with a column projection:

```python
# after: no CQL string, no table name interpolation, and it's async
async def get_jobs_assigned_to_user(cls, user_id: UUID) -> list[dict]:
    return await select_rows(
        cls.find(assignee=user_id),
        "build_id", "start_time", "release_id", "group_id", "assignee", "test_id",
        "id", "status", "investigation_status", "build_job_url", "build_number", "scylla_version",
    )
```

`select_rows` is a two-line Argus helper over coodie's `.only(...).values_list(...)`. Of the 35 raw CQL sites, the only ones left are statements the query builder can't express yet, such as a [`WRITETIME` projection][issue330].


## 2. Pluggable drivers

<img src="{{ site.baseurl }}/assets/img/coodie-drivers.jpg" width="60%" style="float: none; display: block; margin: 0 auto 1.5em;" alt="The coodie mascot plugging four plugs labeled scylla, cassandra, acsylla and rust into a power strip" />

cqlengine lives inside the DataStax-derived driver and can't use anything else. coodie sits on a small driver interface, with four backends today:

- **scylla-driver** (`driver_type="scylla"`, the default): shard-aware, and the recommended choice for ScyllaDB.
- **cassandra-driver** (`"cassandra"`): the upstream DataStax driver.
- **[acsylla]** (`"acsylla"`): async-native, Cython bindings over the C++ driver.
- **[scylladb-rs-driver]** (`"python-rs"`): async-native, the Rust driver exposed through PyO3. Experimental for now.

Switching is one argument:

```python
from coodie.aio import init_coodie

await init_coodie(hosts=["node1", "node2"], keyspace="argus", driver_type="acsylla")
```

Models and queries stay the same. The async-native drivers also work from the sync API through a sync bridge.

Argus uses pluggability differently. It already had a tuned connection, with authentication, a whitelist load-balancing policy and `QUORUM` execution profiles. Rather than open a second connection, it subclassed coodie's driver around the existing session and registered it as the default (trimmed):

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

This is what made a gradual migration possible: cqlengine and coodie shared one session while services moved over one at a time. It also leaves a single place to change drivers later. The migration PR calls `db.py` "the seam for the future acsylla driver swap": one file, not 47 models.

## 3. Pydantic types

<img src="{{ site.baseurl }}/assets/img/coodie-moving-day.jpg" width="60%" style="float: none; display: block; margin: 0 auto 1.5em;" alt="The coodie mascot carrying a box labeled MODELS from a dusty cqlengine filing cabinet to a modern server rack" />

cqlengine predates type hints. This is the Argus `User` model before the migration:

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

A type checker can't tell you what `user.roles` is. Here's the same model in coodie:

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

It's a **Pydantic v2** model with `Annotated` markers for keys and indexes. That brings:

- **Static typing.** Editors and mypy know every field's type, and coodie ships `py.typed`.
- **Validation at the boundary.** Bad data is rejected when the object is built, not when another service reads it later.
- **API integration.** `model_dump()` produces a dict for the API layer, and FastAPI can use the same class as a response model.

Types also made a cleanup worth doing. In [argus#1066][pr1066], key columns and always-populated fields went from `Optional[...]` to required, where the service always writes them and the data held no NULLs. cqlengine has a `required=True` flag too, but it's only checked at runtime. In coodie, `str` versus `Optional[str]` is what both Pydantic and the type checker see, so tightening a field shows every caller that might pass `None` before anything runs.

## Bonus: schema migrations

cqlengine gives you `sync_table()` and wishes you luck. coodie adds a proper schema toolkit on top:

- **`sync_table(dry_run=True)`** returns the CQL it would run instead of running it. Argus used it to check every model against the live cluster: table, type and index names were pinned to what cqlengine had created (including legacy names like `packageversion_v2`), and an empty result meant no data migration was needed.
- **Schema drift warnings** when the database has columns the model doesn't know about.
- **Versioned migration files** for changes `sync_table()` shouldn't guess at, with a CLI to generate, apply, preview and roll them back:

```bash
coodie schema-diff --keyspace argus --module app.models        # what changed?
coodie makemigration --name add_rating --keyspace argus --module app.models
coodie migrate --keyspace argus --dry-run                      # preview the CQL
coodie migrate --keyspace argus                                # apply
```

Changing a field's type is the classic trap: `makemigration` flags it as unsafe instead of emitting an `ALTER`, and the migration file is where you do it properly, by adding a new column, backfilling it with `ctx.scan_table()` (token-range paging, resumable and throttled), and dropping the old one. Runs take a lightweight-transaction lock, so two app instances can't migrate at once, and wait for schema agreement before each DDL statement. Argus didn't need any of this, since it kept its schema as is, but the next change to its schema has a safer path than a hand-written `ALTER TABLE`. See the [schema management guide][schema] for details.

## What production found

The migration surfaced exactly [one coodie issue][issue271]. Everything else ran on coodie as released. A production user and a careful code review catch different bugs, though, so I also ran a [full architecture review][review] afterwards; its findings are fixed in the [1.7.x releases][release].

<!-- TODO(fruch): PLACEHOLDER written in Alexey's style from his PR comments
     (argus#1058, #1059, #1066, #1106). Every claim is from those PRs, but he
     hasn't approved it. Replace with his own words before publishing. -->

> Honestly, I expected the migration to be the scary part. It wasn't - 37 core models, the plugin models and all 18 UDTs moved over one service at a time, and the schema check came back matching cqlengine's table for table (sans one vector index name, which we fixed). Zero data migration. I'll take that.
>
> The fun started after. FastAPI alone got us out of the 1.5 second p99 swamp, but we were still sitting on sync calls, and they were piling up. Flipping the models to `coodie.aio` and throwing the independent reads into `asyncio.gather` is what got us the rest of the way - p99 is now under 100 ms most days, and `submit_run_config` went from over a second to 300 ms. Same database, same schema, just not waiting on things one at a time anymore.
>
> Also, having actual types on the models means the IDE yells at me before production does. Wayy better than finding out from a stack trace.
>
> — Alexey Kartashov, Argus maintainer

## Give coodie a try

<img src="{{ site.baseurl }}/assets/img/coodie-scylladb-family.jpg" width="60%" style="float: none; display: block; margin: 0 auto 1.5em;" alt="A knitted one-eyed ScyllaDB sea monster wearing the coodie beanie and an ARGUS badge, holding a coffee next to a whiteboard mapping DB models to tables and schema" />

Argus now runs on coodie, fully async, on the same schema it had under cqlengine. Thanks to Alexey for being the first production user and for a migration clean enough to serve as the reference example.

coodie lives in the [ScyllaDB GitHub organization][coodie], next to the drivers it builds on. cqlengine, meanwhile, is moving into maintenance mode: bug fixes, but no new features ([docs change in review][pd1127]).

If you use ScyllaDB from Python, we recommend giving coodie a try, for new projects and existing cqlengine code alike. Start with the [migration guide][migration] and the [Argus walkthrough][argus-example], and [open an issue][issues] when something doesn't fit.

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
[schema]: https://scylladb.github.io/coodie/guide/schema-management.html
[bench]: https://scylladb.github.io/coodie/benchmarks/
[pr323]: https://github.com/scylladb/coodie/pull/323
[acsylla]: https://github.com/acsylla/acsylla
[scylladb-rs-driver]: https://github.com/scylladb-zpp-2025-python-rs-driver/python-rs-driver
[issue330]: https://github.com/scylladb/coodie/issues/330
[issue271]: https://github.com/scylladb/coodie/issues/271
[review]: https://github.com/scylladb/coodie/blob/master/docs/reviews/2026-10-architecture-review.md
[release]: https://github.com/scylladb/coodie/releases
