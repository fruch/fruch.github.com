---
layout: post
title: "Taming the logging formatter"
description: ""
category: 
tags: [python,logging]
---
{% include JB/setup %}

We love logging, and we use it all around our code. (it's the standard/built-in/batteries included)

We have those hugh json objects flying around, we want to log them.

pprint.pformat comes handy for those cases:

{% highlight python %}

import pprint
my_large_data = [ dict(data="my large inforamtion", data1="dicts, dicts, dicts,", data3=dict(a="??", b=2, c=3, d="***")),
                  dict(data="my large inforamtion", data1="how we love big dicts ?", data3=dict(a="??", b=2, c=3, d="***")),
                  dict(data="my large inforamtion", data1="how we love big dicts ? don't we ?,", data3=dict(a="???", b=2, c=3, d="***")),
                ]

logger.error("Mary \n had \n a \n little \n lamb")
logger.error(pprint.pformat(my_large_data))
logging.error(pprint.pformat(my_large_data))
{% endhighlight %}

but when used with complex formatter the output goes like that:

    ^14/11/06 00:58:39 !ERROR <t:MainThread T:root M:log.py F:<module> L:74 > Mary
     had
     a
     little
     lamb
    ^14/11/06 00:58:39 !ERROR <t:MainThread T:root M:log.py F:<module> L:75 > [{'data': 'my large inforamtion',
      'data1': 'dicts, dicts, dicts,',
      'data3': {'a': '??', 'b': 2, 'c': 3, 'd': '***'}},
     {'data': 'my large inforamtion',
      'data1': 'how we love big dicts ?',
      'data3': {'a': '??', 'b': 2, 'c': 3, 'd': '***'}},
     {'data': 'my large inforamtion',
      'data1': "how we love big dicts ? don't we ?,",
      'data3': {'a': '???', 'b': 2, 'c': 3, 'd': '***'}}]
    ^14/11/06 00:58:39 !ERROR <t:MainThread T:root M:log.py F:<module> L:76 > [{'data': 'my large inforamtion',
      'data1': 'dicts, dicts, dicts,',
      'data3': {'a': '??', 'b': 2, 'c': 3, 'd': '***'}},
     {'data': 'my large inforamtion',
      'data1': 'how we love big dicts ?',
      'data3': {'a': '??', 'b': 2, 'c': 3, 'd': '***'}},
     {'data': 'my large inforamtion',
      'data1': "how we love big dicts ? don't we ?,",
      'data3': {'a': '???', 'b': 2, 'c': 3, 'd': '***'}}]

Kinda, not really helpful:

1. *confusing* - and you loose track of where this print came from really fast (keep in mind I'm talking about humongous json object)
1. *filtering* is (almost) impossible (yeah, not without some extra regex kung-fu)

Skimmed through the logging documentations, google it a bit think someone already solved those things
and I could copy paste, came out empty handed.

So here how it can be fixed:

{% highlight python %}

import sys
import logging


class MultiLineFormatter(logging.Formatter):

    def format(self, record):
        """
        split the message into different line and prepend it with the formatting
        :param record:
        :return: the formatted string
        """
        output = []

        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)

        data = dict(**record.__dict__)

        message = record.getMessage()
        for msg in message.split('\n'):
            data['message'] = msg
            output += [self._fmt % data]

        s = "\n".join(output)

        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            if s[-1:] != "\n":
                s = s + "\n"
            try:
                s = s + record.exc_text
            except UnicodeError:
                # Sometimes filenames have non-ASCII chars, which can lead
                # to errors when s is Unicode and record.exc_text is str
                # See issue 8924.
                # We also use replace for when there are multiple
                # encodings, e.g. UTF-8 for the filesystem and latin-1
                # for a script. See issue 13232.
                s = s + record.exc_text.decode(sys.getfilesystemencoding(),
                                               'replace')

        return s

# and two examples how to configure the root logger to use it

import logging
import logging.config

logger = logging.getLogger()
logging.basicConfig()

def configure_with_api():
    handler = logging.StreamHandler()
    formatter = MultilineFormatter(fmt='^%(asctime)s !%(levelname)s <t:%(threadName)s T:%(name)s M:%(filename)s F:%(funcName)s L:%(lineno)d > %(message)s',
                                  datefmt='%y/%m/%d %H:%M:%S')
    handler.formatter = formatter
    logger.addHandler(handler)

def configure_with_dictConfig():

    logging.config.dictConfig( {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'multiline': {
                '()' : MultilineFormatter,
                'format': '^%(asctime)s !%(levelname)s <t:%(threadName)s T:%(name)s M:%(filename)s F:%(funcName)s L:%(lineno)d > %(message)s',
                'datefmt': '%y/%m/%d %H:%M:%S'
            },
        },
        'handlers': {
            'console':{
                'class':'logging.StreamHandler',
                'formatter': 'multiline'
            },
        },
        'loggers': {
            '': {
                'handlers':['console'],
                'propagate': True,
                'level':'INFO',
            },
        }
    }
    )
{% endhighlight %}

and now our output is much much clearer:

    ^14/11/06 00:54:51 !ERROR <t:MainThread T:root M:log.py F:<module> L:74 > Mary
    ^14/11/06 00:54:51 !ERROR <t:MainThread T:root M:log.py F:<module> L:74 >  had
    ^14/11/06 00:54:51 !ERROR <t:MainThread T:root M:log.py F:<module> L:74 >  a
    ^14/11/06 00:54:51 !ERROR <t:MainThread T:root M:log.py F:<module> L:74 >  little
    ^14/11/06 00:54:51 !ERROR <t:MainThread T:root M:log.py F:<module> L:74 >  lamb
    ^14/11/06 00:54:51 !ERROR <t:MainThread T:root M:log.py F:<module> L:75 > [{'data': 'my large inforamtion',
    ^14/11/06 00:54:51 !ERROR <t:MainThread T:root M:log.py F:<module> L:75 >   'data1': 'dicts, dicts, dicts,',
    ^14/11/06 00:54:51 !ERROR <t:MainThread T:root M:log.py F:<module> L:75 >   'data3': {'a': '??', 'b': 2, 'c': 3, 'd': '***'}},
    ^14/11/06 00:54:51 !ERROR <t:MainThread T:root M:log.py F:<module> L:75 >  {'data': 'my large inforamtion',
    ^14/11/06 00:54:51 !ERROR <t:MainThread T:root M:log.py F:<module> L:75 >   'data1': 'how we love big dicts ?',
    ^14/11/06 00:54:51 !ERROR <t:MainThread T:root M:log.py F:<module> L:75 >   'data3': {'a': '??', 'b': 2, 'c': 3, 'd': '***'}},
    ^14/11/06 00:54:51 !ERROR <t:MainThread T:root M:log.py F:<module> L:75 >  {'data': 'my large inforamtion',
    ^14/11/06 00:54:51 !ERROR <t:MainThread T:root M:log.py F:<module> L:75 >   'data1': "how we love big dicts ? don't we ?,",
    ^14/11/06 00:54:51 !ERROR <t:MainThread T:root M:log.py F:<module> L:75 >   'data3': {'a': '???', 'b': 2, 'c': 3, 'd': '***'}}]
    ^14/11/06 00:54:51 !ERROR <t:MainThread T:root M:log.py F:<module> L:76 > [{'data': 'my large inforamtion',
    ^14/11/06 00:54:51 !ERROR <t:MainThread T:root M:log.py F:<module> L:76 >   'data1': 'dicts, dicts, dicts,',
    ^14/11/06 00:54:51 !ERROR <t:MainThread T:root M:log.py F:<module> L:76 >   'data3': {'a': '??', 'b': 2, 'c': 3, 'd': '***'}},
    ^14/11/06 00:54:51 !ERROR <t:MainThread T:root M:log.py F:<module> L:76 >  {'data': 'my large inforamtion',
    ^14/11/06 00:54:51 !ERROR <t:MainThread T:root M:log.py F:<module> L:76 >   'data1': 'how we love big dicts ?',
    ^14/11/06 00:54:51 !ERROR <t:MainThread T:root M:log.py F:<module> L:76 >   'data3': {'a': '??', 'b': 2, 'c': 3, 'd': '***'}},
    ^14/11/06 00:54:51 !ERROR <t:MainThread T:root M:log.py F:<module> L:76 >  {'data': 'my large inforamtion',
    ^14/11/06 00:54:51 !ERROR <t:MainThread T:root M:log.py F:<module> L:76 >   'data1': "how we love big dicts ? don't we ?,",
    ^14/11/06 00:54:51 !ERROR <t:MainThread T:root M:log.py F:<module> L:76 >   'data3': {'a': '???', 'b': 2, 'c': 3, 'd': '***'}}]

**Disclaimer: use with caution, written past midnight :)**