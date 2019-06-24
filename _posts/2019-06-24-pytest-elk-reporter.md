---
layout: post
title: "Introducing pytest-elk-reporter"
description: ""
category:
tags: [elasticsearch, python, pytest, plugin]
---
{% include JB/setup %}

# pytest-elk-reporter

**tl;td**: https://github.com/fruch/pytest-elk-reporter

## History
Few years back I've wrote a post about how I've connected python based test to ELK setup - ["ELK is fun"](http://fruch.github.io/blog/2014/10/30/ELK-is-fun), it was using an xunit xml, parsing it and sending it via Logstash.

Over time I've learn a lot about ElasticSearch and it's friend Kibana, using them as a tool to handle logs. and also as a backend for a search component on my previous job.

So now I know logstash isn't needed for reporting test result, posting straight into elasticsearch is easier and gives you better control, ES is doing anything "automagiclly" anyhow nowadays.

## What can it do ?

* **collect** as much information as you can about one test results and running environment and send it to elasticsearch.
    * data like git commit/sha from current directory
    * jenkins environment variables, like job id and username triggered the job.
    * cool tracebacks which pytest excels at.

* **extend** - let user configure (like target address and credentials) it from code, and add data of their own to each session or test.

## Tricks I've picked on the way

Every time I start a new package, I learn a few new things, here's a few I'm happy about this time:

* Created the package with [cookiecutter-pytest-plugin](https://github.com/pytest-dev/cookiecutter-pytest-plugin)

* I'm using [pre-commit](https://pre-commit.com)

    * [black](https://github.com/python/black) - instead of the old friend [autopep8](https://github.com/hhatto/autopep8).

    * [pylint](https://www.pylint.org/) in both python27 and python36 to keep the code clean of silly mistakes.
    
* [Travis](https://travis-ci.org/fruch/pytest-elk-reporter)

    build and test with Tox on all possible python versions.
    
    also uploading wheels to pypi based on tags.
    
    thanks to [setuptools_scm](https://github.com/pypa/setuptools_scm) version no need to edit files for setting version number.

* [Appveyor](https://ci.appveyor.com/project/fruch/pytest-elk-reporter)

    I also cover windows own little issue (non found so far).

* [Codecov](https://codecov.io/gh/fruch/pytest-elk-reporter/commits)

    really like that it can collect from multiple run, for example both linux and windows tests run, which helps to show the total coverage. 
    
    got me to 93% line coverage (and going down as I add more code).

# The bad stuff - a.k.a things I need to improve

* **Documentation** - I've mostly wrote test, zero docs.

* **Name** - it's a bit boring, and might conflict with other plugins.

* **Kibana Dashboards examples**

    I should really include some sample kibana dashboard to show the strength of it, it's own test data is a bit boring.

* **auto generating and upload of docs**

    I've tried using Travis Deploy to github Pages, didn't exactly nailed, or got it working as I expect, maybe I should try [readthedocs](https://readthedocs.org/).

* **pytest-xdist** 

    I still need to test it with xdist, it's going to make thing a more tricker, as usual.

## What you should next

Go grab [it](https://github.com/fruch/pytest-elk-reporter), git it a star, fork it.

I'm waiting for your PRs, and your stories on how it's help you tame a whole bunch of tests.

{% highlight bash %}

    # forgot to show how to install :\
    pip install pytest-elk-reporter
{% endhighlight %}