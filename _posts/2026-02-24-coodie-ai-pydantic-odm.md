---
layout: post
title: "Coodie: A 4-year-old idea brought to life by AI (and some coffee)"
description: "How a half-baked repo from 4 years ago finally became a real Pydantic ODM for Cassandra/ScyllaDB, thanks to our new robot overlords."
category: python
tags: [python, cassandra, scylladb, ai, open-source, pydantic]
---

So, let's rewind a bit. About four years ago, I was looking at [Beanie] — this really nifty, Pydantic-based ODM for MongoDB. And as someone who spends an unhealthy amount of time deep in the trenches of ScyllaDB and Cassandra, I had a thought: "Where is *my* Beanie? I want a hoodie, but for Cassandra." And thus, the name was born: **coodie** = **c**assandra + beanie (h**oodie**). Catchy, right?

Like any respectable developer, I rushed to GitHub, created the repository [fruch/coodie], maybe wrote a highly ambitious `README.md`, set up a `pyproject.toml`, and then... absolutely nothing. Crickets. Life happened. I had CI pipelines to fix, Scylla drivers to maintain, conferences like PyConIL and EuroPython to attend, and live-tweeting to do. coodie just sat there, gathering digital dust, a glorious monument to my good intentions and severe lack of free time.

## Fast forward to today. The AI era.

We are living in a weird timeline where LLMs are everywhere, threatening to take our jobs while simultaneously failing to center a div. People are talking about AI coding assistants non-stop. I myself was quite happy with my usual workflow, but I figured — why not take my 4-year-old fever dream for a walk in the park and feed it to the machine?

I threw the basic concept at an AI. I gave it some ground rules: it has to use Pydantic v2, it needs to be backed by [scylla-driver], and it needs to feel as magical as Beanie.

And holy crap. It actually worked.

I spent four years procrastinating on this, and a glorified autocomplete bot basically bootstrapped the whole thing while I was sipping my morning coffee. I'm not sure if I should be proud of my newfound status as a "prompt engineer," or slightly terrified that my open-source street cred is now partially owned by a matrix of weights and biases.

## The sweet setup we have now

Despite the AI doing the heavy lifting, the architecture actually makes a lot of sense. Here is what coodie brings to the table:

- **Pydantic v2 all the way**: Define your documents with full type-checking support.
- **Declarative schemas**: You just annotate fields with `PrimaryKey`, `ClusteringKey`, `Indexed`, or `Counter`.
- **Automatic table management**: You call `sync_table()` and it creates or evolves the table idempotently. No more writing raw CQL just to add a column.
- **Sync and Async APIs**: Because why choose? You can use `coodie.aio` if you are riding the asyncio train, or `coodie.sync` if you want blocking code.
- **Chainable QuerySets**: Doing `await Product.find(brand="Acme").limit(10).all()` just feels right.

Here is a quick taste of what the AI and I managed to cook up:

```python
from typing import Annotated
from uuid import UUID, uuid4
from pydantic import Field
from coodie import Document, init_coodie, PrimaryKey

class Product(Document):
    id: Annotated[UUID, PrimaryKey()] = Field(default_factory=uuid4)
    name: str
    price: float = 0.0

    class Settings:
        keyspace = "my_ks"
```

And then querying it is a breeze:

```python
# async
products = (
    await Product.find()
    .filter(brand="Acme")
    .order_by("price")
    .limit(20)
    .all()
)
```

## Wrapping up

The AI works out of the box with almost zero friction. It's very impressive, and honestly, a bit surreal to see an idea you abandoned years ago suddenly have a passing CI suite, complete with tests and GitHub Actions (which are still very tidy to look at, by the way).

You can check out the code, star it, or fork it over at [github.com/fruch/coodie].

PRs are welcome. Preferably written by humans, but honestly... I guess I can't really enforce that anymore, can I? יאללה, let's see how it goes.

[Beanie]: https://github.com/roman-right/beanie
[fruch/coodie]: https://github.com/fruch/coodie
[scylla-driver]: https://github.com/scylladb/python-driver
[github.com/fruch/coodie]: https://github.com/fruch/coodie
