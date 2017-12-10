---
layout: post
title: "Microsoft + Docker, really ?"
description: ""
category: 
tags: [docker, microsoft, linux]
---
{% include JB/setup %}

Today [this][1] blog post of Scott Guthrie from Microsoft was slash-dotted.
Interesting enough, I had no idea one can actually run Docker on Windows, got me to find that there's an [installer][2],

From the details, I couldn't figure if that's mean we could actually spin a windows docker host, and run linux based dockerized apps ?
even if it's intended only for running windows based dockerized apps, it's an interesting match which I think I'll might find handy in the future.

Docker is really interesting, but it got a very weird edges. 3 examples:

1. When your host is 64bit, and you need a 32bit application. it's not that easy to setup up, I've tried couple of time and failed.
1. Anther weird stuff I've run into was this [issue][3], (don't ask why I need to manually change /etc/hosts, It's a sad answer) but some kind of limitations are in place, and might drive away arguing things like "Change hosts and resolv is the basic operation in daily working."
1. Entering a docker you've created, C`mon is should be a bit easier and integrated into docker (and not that long command line to remember)

Anyhow the whole experience with docker is very nice, and I do recommend giving it a spin. (you'll sure put this one in your toolbox/toolbelt)

[1]: http://weblogs.asp.net/scottgu/docker-and-microsoft-integrating-docker-with-windows-server-and-microsoft-azure
[2]: https://docs.docker.com/installation/windows/
[3]: https://github.com/docker/docker/issues/2267