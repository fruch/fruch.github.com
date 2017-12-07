---
layout: post
title: "Microsoft - amazing stuff, WSL, VSCode"
description: ""
category:
tags: [windows, linux, wsl, vscode, docker]
---
{% include JB/setup %}

# WSL

I've took [WSL](https://en.wikipedia.org/wiki/Windows_Subsystem_for_Linux) for a spin today, and I'm impressed.

```
# doing something like this
$ apt install docker.io
```

Actully worked, i.e. installed. you can't start the dockerd as failed as in [#2291](https://github.com/Microsoft/WSL/issues/2291)

But you can use the docker client, and connect a server running dockerd (or in win10 pro the native docker supported)

The direction is quite good, I can have tmux and my favorite nano working stright on my windows box like that.

Still didn't figured out how to leave things running, like my tmux session (if at all possible)

# VSCode

Anthoer supprise from microsoft (I guess it's not that new, just new to me), is [VSCode](https://code.visualstudio.com/)

I hated visual studio for year, and this one is fully open source based on node.js, resembles more atom.

List of goodies I have with it:

* **markdown previews**
* **spellchecker**
* **python pylint** - based on my config files, and not as in Pycharm own code style checks.
* **node linting** - again working with my config (I guess WebStorm has it too, but it's not free)
* **[plantuml](http://plantuml.com/) preview** - amazing for documention
* **terminal** can use gitbash inside of it

The marketplace of plugings, is also quite nice, and sits in a very front and center place (looking at you jetbrains, suggestion is nice, but getting to the list of plugin is a bit long)

The updates are a bit more plesent then in Jetbrain products, and comes with great webcast on each major feature. (giving us a very good lesson on writing release notes :))

And also people are pushing to have it running under WSL [#2293](https://github.com/Microsoft/WSL/issues/2293)

# Conclusion

I see a very bright future for microsoft steping into the core thing that the development community are looking at.

Microsoft, i'm keeping my ears and eyes open... 

You got my attention !
