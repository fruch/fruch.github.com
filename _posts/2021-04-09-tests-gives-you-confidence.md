---
layout: post
title: "Tests gives you confidence - But data gives you power"
description: ""
category:
tags: [python, pycon.il, elasticsearch, pytest]
---
{% include JB/setup %}

# Tests gives you confidence - But data gives you power

## Who Am I

* Israel Fruchter, I'm working in testing for the past 15 year. previusly on the television and home entertiment domain, and nowdays at scylladb.

## What's broken about test reporting

As we all know, most of the testing frameworks we use and love, were written with the intention of running those quick and very precise unit test

But then reality come knocking, products evolves, teams expend, microservices spawns. And you find yourself with silly amount of those functional or integration or selenium based tests, with run runtime of 30secs to 1 hour each, that you are running almost 24/7. Lots information get spit at back you, and you want to collect it put some order into it. see it clearly.

So you look for the defacto standard of reporting from unittest runners, and bam, junit X M L.

You feed it into your CI system, assuming we are all set to go.

(Oh boy someone was naive...)

* In lots CI systems, test report are not exactly first class citizen (if exist at all)

* Test runner have the tendecy to generate the junit.xml only when the whole test session is finished (the horror finding out the 12 hours timeout to you jenkins job, results)

[facepalm gif]

## pytest-elk-reporter enters the stage

So in most case it becomes clear you want to throw your test information into some database.

We'll skip the story of the poor guy doing that with SQL.

We'll also gonna skip the gazillion Jira like tools that you assumed will be the canonical answer for test reporting. They are probably not exactly what you hoped for.

So if you did the sensible choice and you are using pytest, let cover what this plugin can do for you.

The idea quite simple, each single test result is going to be sent out to elasticsearch, right as the test finishes.

You just need to point it to a running elasticsearch, and your set to go.
```python
from pytest_elk_reporter import ElkReporter

def pytest_plugin_registered(plugin, manager):
    if isinstance(plugin, ElkReporter):
      # TODO: get credentials in more secure fashion programmatically, maybe AWS secrets or the likes
      # or put them in plain-text in the code... what can ever go wrong...
      plugin.es_address = "my-elk-server.io:9200"
      plugin.es_user = 'fruch'
      plugin.es_password = 'passwordsarenicetohave'
      plugin.es_index_name = 'test_data'
```

What you actually would get is in elastic automatically is contextual data to each test.

Information as git branch or last commit and technically what ever you CI system is exposing (if it's Jenkins/Travis/Circle CI or github actions)
And you could add you own user data into the context that is sent to Elastic, with fixtures built for that. on a test level, or a test session level.

Sprinkle a bit of Kibana magic ontop of it, you get this:

[dashboard print screen]

A cool customized dashboard tailor just for you (assuming you know what you want to see)
that get updated in real time as your test suite is running, holding weeks months or years of you test data history.

You want to collect the response time of one specific API call, from your test, and graph it based on time or versions to spot regressions ? checked.

You want to visualize your tests base on the markers you are using ? checked.

## Now we can shift gears

Remember the horror story with the 12h timeout.
Why in the first place we have a test session of 12h.

Can't we do much better by splitting our tests across the cloud VMs (or AWS spot fleet) and getting it done in one hour ?

So let assume we have 2000 tests to run like that. but how do we split it ? based on what exactly ?

If only we could group tests based on their past known durations, [mic drop gif]: 

```
# pytest --collect-only --es-splice --es-max-splice-time=4 --es-default-test-time=60
...

0: 0:04:00 - 3 - ['test_history_slices.py::test_should_pass_1', 'test_history_slices.py::test_should_pass_2', 'test_history_slices.py::test_should_pass_3']
1: 0:04:00 - 2 - ['test_history_slices.py::test_with_history_data', 'test_history_slices.py::test_that_failed']

...

# cat include000.txt
test_history_slices.py::test_should_pass_1
test_history_slices.py::test_should_pass_2
test_history_slices.py::test_should_pass_3

# cat include000.txt
test_history_slices.py::test_with_history_data
test_history_slices.py::test_that_failed

### now we can run each slice on it's own machine
### on machine1
# pytest $(cat include000.txt)

### on machine2
# pytest $(cat include001.txt)
```

## take away

* Careful with mix the types on context info you are adding, if it's a string, don't ever change it into a number and vice verse, Kibana doesn't know how to ducktape.

* Try not adding too much nesting into context data, your future self would appreciate it when building visualizations on Kibana

"And do trust me on the sunscreen"


## Background and Context

• Cisco - big project 20 scrum teams - agile transformation
• lot of test are written and becomes part of the gating of the project
• tests are slow, and not really stable  (cause of bunch of reasons , Selenium based tests, team that are writing backends for the first time)

## Challenge, complication, problem

• tests suite are getting complicated, and investigating the gating test becomes complex more and more, and involved multiple teams, slowing the project to almost complete halt 

## Change, breakthrough

• collecting the date in ELK, all test marked with with clear ownership 
• one look at a kibana dashboard and you can send a link to the responsible team, so they can address it.

## Outcome

* The test data become a vital part of the project, and to the speed 
the project can move

## Message

• Collecting test data, can vital to a project.







## Introduction 

* Did you ever found yourself chase a flaky test down  the rabbit hole ? 

* how do you know a test is flaky ? 

* 1% failure rate ?  10% failure ?

* where you get the information from ?

I'm Israel Fruchter, and I'm a Test and Automation Team Leader in Scylladb
and author of the open source project `pytest-elk-reporter`

Today we'll try to show how simple it is to collect test information out
of pytest runs, and use it on to learn more things about your tests.
(and also a bit of the origin story of that project)

This would be a short talk, you can hit me later on the venues or at tweeter if you have more questions 

# Timeout story

## Background and Context

* We have this poor scylladb developer - we'll name him Mike 
* That need to handle an increasing number of functional tests
* long running integration tests running from 30sec - 1h (not you the common unittest)
* Around  ~3500 of them
* Those are running almost 24/7
* Lots information get spit at back you mostly into console 

## Challenge, complication, problem

* He feed it into your CI system, and letting the test loose. 
* And he find himself with silly amount of data
* And then one morning: He finds out the 12 hours timeout on a jenkins job, and he has not data

[facepalm gif]

# few facts on continues integration (CI) system and tests

* testing frameworks/runner are written with the intention of running quick/small unit tests
* for long integration tests (functional / integration / selenium based tests), they are a bit less helpful
* CI systems, test report are not exactly first class citizen (if exist at all, github actions i'm looking at you...)
* The defacto "standard" of results runners, is junit/nunit **XMLs**. (which year is this ??)
* Test runner have the tendency to generate the junit.xml only when the whole test session, if **finished**

## Lets introduce pytest-elk-reporter (Change, breakthrough)

* clearly he wants the test information saved somewhere else (not in the continues integration (CI) system).
* We'll skip part he's fighting with a SQL DB of some kind.
* We'll skip part he's hand wrestling with Jira and the likes of it (even sadder story).

So here's comes `pytest-elk-reporter`, lets cover what it has for him: 

* send the test information to elasticsearch
* each single test result is going to be sent out, right as the test finishes.
* all information CI system is exposing (Jenkins/Travis/Circle CI or github actions) would be available

* installation:
[setup slide]

* just connect it to a running elasticsearch, and your done. 

## Outcome

* now it's being used in two of scylladb functional test repositories 
* Mike can pin quickly every test breakage 
* Mike can handle stability issues with actual data, and not hand waving
* Mike can add any data from any test, and get it into the dashboard, with ease.
* and do much more - keep tuned

[slides of the dashboard]

## Message

Save you test data, it gonna worth you a fortune
and next part gonna touch exactly on that - "Running test on spot instances" 
