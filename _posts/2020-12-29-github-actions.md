---
layout: post
title: "Taking Github Actions for a walk in the park"
description: ""
category:
tags: [python, github-actions, ci, travis]
---
{% include JB/setup %}

# Taking Github Actions for a walk in the park

## Travis started to scare me a bit

People were talking about github actions for a while now, lot of hype around it.
I myself was quite happy with the things I've managed to get done with [Travis].

But then came in this announcement from travis: ["The new pricing model for travis-ci.com"].
I was reading via lot of the backlash in tweeter about it, and after carefully reading the announcement itself, I was starting to think that the work I did for [scylla-driver] was counting on [Travis] too much.

Recently I've start seeing long queues for job triggers in travis, and I was starting to have second thoughts about picking travis. (not so long ago, less than a year ago)

## The sweet setup I had in Travis

As a recap for [scylla-driver], since it's a c based package, heavily using [cython].
We are building python wheels for windows, mac, linux, ranging from python2.7 to python3.9, and pypy. (also using the [Travis] experimental aarch64 and ppc64le support)

For building the wheels we are using [cibuildwheel], which is a nifty tool that magically keep all know how, on how building wheels correctly on multiple platforms.
In linux, it's using the official docker images provided by the [Python Packaging Authority
] for manylinux2014.
And on windows and mac equivalents with the correct set to needed tool to get you wheel happily containing all the need dynamic libraries it depended on

[cibuildwheel] also comes with readily available examples for all the major CI system out there

<a href="https://travis-ci.org/github/scylladb/python-driver/builds/709882917"><img src="{{ site.url }}/assets/img/python-driver-release.png" width="100%" /></a>

[cibuildwheel] is also helping you in running unittest ontop of each built wheel (since in my case the setup is a bit complex, getting it installed and compile across the board was hard, we we're skipping some unittest on some platforms)

Travis was also running our integration test suite, and running it on our PRs, and automatically uploading all the wheels and source distribution to Pypi.

I was working on this setup for long week, with a tight deadline for it to be ready for [europython2020], thanks to [@ultrabug]

## Github actions

For a while I was a bit unsure if it would be a match to what I had in travis. But one day our own Jenkins server was down for maintenance, and a big portion of my day was clear case of that.

I've started with copy-pasting [cibuildwheel] github actions [example], and worked my way from there.

When I've started adding all the different unittest and platforms, I was struggling a bit with how the matrix is working, and how conditional steps works.

It ended up something like this, almost identical to what I had in travis:

```yaml
name: Build and upload to PyPi

on: [push, pull_request]

env:
  ...

jobs:
  build_wheels:
    name: Build wheels ${{ matrix.os }} (${{ matrix.platform }})
    if: contains(github.event.pull_request.labels.*.name, 'test-build') || github.event_name == 'push' && endsWith(github.event.ref, 'scylla')
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        include:
          - os: ubuntu-18.04
            platform: x86_64

          - os: ubuntu-18.04
            platform: i686

          - os: ubuntu-18.04
            platform: PyPy

          - os: windows-latest
            platform: win32

          - os: windows-latest
            platform: win64

          - os: windows-latest
            platform: PyPy

          - os: macos-latest
            platform: all

          - os: macos-latest
            platform: PyPy

```

We had a nice twist that we didn't have before, but now we can control from github PR which part of my pipeline would run using label, since github actions is so tightly integrated you can lookup almost anything related to the PR.

## Github Actions - UI

This is how the final thing looks like:
<a href="https://github.com/scylladb/python-driver/actions/runs/446668339"><img src="{{ site.url }}/assets/img/github_actions.png" width="100%" /></a>

logging is a bit weird to watch while it's running, but after the fact the log are very tidy to look at

## Late surprise - cross compile using qemu

With almost perfect timing I've run into this
https://github.com/joerick/cibuildwheel/pull/482
by [Pavel Savchenko](https://github.com/asfaltboy)

I was trying all kind of things to get aarch64 support, but this PR figure it out quite nicely, with one magic step:

```yaml
- name: Set up QEMU
id: qemu
uses: docker/setup-qemu-action@v1
with:
    platforms: all
```

For reference the full [workflow](https://github.com/scylladb/python-driver/actions/runs/446668338/workflow)

Now we can have docker using qemu to run docker instances based on different cpu architecture, it's horribly slow but it's working.

And nice side effect I've learned how to run it locally, so I can debug those things. Something I haven't figured when running with Travis, apparently travis was using the same trick on their experimental support for those architectures.

## Summary

Github actions works out of the box, with almost zero fraction, almost anything I could think about I've found a readily available step I can pickup, very impressing.

One thing I haven't yet tried out, is using self hosted runner, hopefully I won't need it.
Cause who want to babysit anther server on his own, or worse, a bunch of them.

[scylla-driver]: https://github.com/scylladb/python-driver
[Travis]: https://travis-ci.org/
["The new pricing model for travis-ci.com"]: https://blog.travis-ci.com/2020-11-02-travis-ci-new-billing
[cibuildwheel]: https://github.com/joerick/cibuildwheel
[cython]: https://cython.org/
[Python Packaging Authority]: https://www.pypa.io/en/latest/
[python-driver-release]: https://travis-ci.org/github/scylladb/python-driver/builds/709882917
[example]: https://cibuildwheel.readthedocs.io/en/stable/setup/#github-actions
[europython2020]: https://ep2020.europython.eu/
[@ultrabug]: https://twitter.com/ultrabug
