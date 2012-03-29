---
layout: post
title: "Highlights from pyvideo.org"
description: ""
category: Blog
tags: [python]
---
{% include JB/setup %}

Look like people were quite busy in the latest [US PyCon](https://us.pycon.org/2012/), 
I need to promise myself to actully attand one in the next coming years.
too bad there no such thing in IL, to only closest thing is the meetups of [PyWeb-IL](https://groups.google.com/forum/?fromgroups#!forum/pyweb-il) 
(I want to attand one also..., even thought on trying to host one at my day job office)

So thanks to the people of [pyvideo.org](http://pyvideo.org/), we could actully see what was going on.

## Frozen Yogort ##
I've seen ["Esky: keep your frozen apps fresh"](http://pyvideo.org/video/470/pyconau-2010--esky--keep-your-frozen-apps-fresh)
this guy really touch the spot, on how to deliver the code to mortal that can't handle the python interpeter.

Amazing how it can be done with three line of code (yes, and anthor two in the *setup.py*):

{% highlight python %}
if hasattr(sys,"frozen"):
	app = esky.Esky(sys.executable,"http://example.com/downloads/")
	app.auto_update()
{% endhighlight %}

go fetch it from PyPi, *[esky](http://pypi.python.org/pypi/esky/)*

## RESTful APIs for the tired ##

In this [One](http://pyvideo.org/video/90/djangocon-2011--building-apis-in-django-with-tast),
it show how easy is to add RESTful API to a django application.

Cery useful if you want to keep those control freaks nerds happy, 
now they could write a bash script that uses curl to interact with your site.