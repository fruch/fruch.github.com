---
layout: post
title: "Highlights from pyvideo.org"
description: ""
category: Blog 
tags: [python, testing]
---
{% include JB/setup %}

Look like people were quite busy in the latest [US PyCon][1], 
I need to promise myself to actually attend one in the next coming years.
too bad there no such thing in IL, to only closest thing is the meetups of [PyWeb-IL][2] 
(I want to attend one also..., even thought on trying to host one at my day job office)

So thanks to the people of [pyvideo.org][3], we could actually see what was going on.

[1]: https://us.pycon.org/2012/
[2]: https://groups.google.com/forum/?fromgroups#!forum/pyweb-il
[3]: http://pyvideo.org/

## Frozen Yogort ##
I've seen "[Esky: keep your frozen apps fresh][4]", this guy really touch the spot, 
on how to deliver the code to mortal that can't handle the python interpeter.

Amazing how it can be done with three line of code (yes, and anthor two in the *setup.py*):


{% highlight python %}
if hasattr(sys,"frozen"):
	app = esky.Esky(sys.executable,"http://example.com/downloads/")
	app.auto_update()
{% endhighlight %}

go fetch it from PyPi, *[esky][5]*

[4]: http://pyvideo.org/video/470/pyconau-2010--esky--keep-your-frozen-apps-fresh
[5]: http://pypi.python.org/pypi/esky/

## RESTful APIs for the tired ##

In [this One][6],
it show how easy is to add RESTful API to a django application.

Very useful if you want to keep those control freaks nerds happy, 
now they could write a bash script that uses curl to interact with your site.

[6]: http://pyvideo.org/video/90/djangocon-2011--building-apis-in-django-with-tast

## Fast Test, Slow Test ##

And a one about testing, casue my job title dictates it.
 
[Fast Test, Slow Test][7], by [Gary Bernhardt][8]
(really liked his [dotfiles][9] repo)

I really agreed with almost every word he were saying, too bad it really is 
a pain actully writing unittests that hit the right spots.
his saying about not writing tests to "bake" the bad desgin into the system, 
reminded me what i'm doing almost daily. 
Writing tests to match requirements or other system behivers that are actully 
wrong or will do more bad then good in the system.

But then, who has to power/will to change a big eco system upside down ? 

Think of it, one of the tester that work at Microsoft on a new version of Windows, 
will come and say that the briliant people who thought and desgin something we're wrong.
He will probably give up, every before that thought will touch the first neuron in his brain...

We all want to come home in one piece ( [בסך הכל רציתי לחזור הביתה בשלום][10])

[7]: http://pyvideo.org/video/631/fast-test-slow-test
[8]: https://github.com/garybernhardt
[9]: https://github.com/garybernhardt/dotfiles
[10]: http://www.givathatachmoshet.org.il/songs.php?song=song1.flv
