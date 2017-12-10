---
layout: post
title: "KISS - Keep it shorter short"
description: ""
category: 
tags: [python]
---
{% include JB/setup %}

Today on work on a python related mailing list someone sent this snippet of code he didn't wrote.
and that was causing some of the server he worte/manged some troubles.

Here's the code:

{% highlight python %}

    def deploy_file(full_path_to_file, full_path_in_server):
        if full_path_to_file is None or full_path_in_server is None or full_path_to_file == "" or full_path_in_server == "":
            print_error_exit(" wrong input for deploy_file")
        try:
            post_status = None
            with open(full_path_to_file, mode="rb") as f:
                print ("Deploying...:  %s" % full_path_in_server)
                file_content = f.read()
                post_status = requests.put(url= full_path_in_server, data=file_content)
                if post_status.status_code == 200 or post_status.status_code == 201 or post_status.status_code == 202:
                    print ("Success:  %s" % full_path_in_server)
                    return {"uploaded": file_to_upload }
                else:
                    print_error_exit ("Deployment to %s failed. status_code = %s, returned_text = %s" % (full_path_in_server, post_status.status_code, post_status.text))
        except Exception as ex:
            print (ex)
            print_error_exit ("Posting with url %s failed. status: %s" % (full_path_in_server, post_status))
{% endhighlight %}

First thought I hade was, the one wrote it is must be coming from C (or maybe Java), so let go over what's wrong here.

1. Input validation

    I don't know what's print_error_exit() is doing exactly, let's assume it's raising expection (hopefully it's not calling os.exit())    
    So assertion with the proper text would be alsmot identical.

    Checking both for None, and for empty string is futile, just assert, like this:

    {% highlight python %}
        assert full_path_to_file, "parameter can't be empty"
        assert full_path_in_server, "parameter can't be empty"
    {% endhighlight %}

1. Using requests to stream file

    Requests is cool, alsmot the defacto standard when HTTP client is need in python.
    it has very good documention, clearly someone didn't read it.[streaming uploads][1]

1. Multiple error paths

    Lot of different error handling code, one for checking the http statuses and one for catching expections.

# My version

{% highlight python %}

    def deploy_file(full_path_to_file, full_path_in_server):
        assert full_path_to_file, "parameter can't be empty"
        assert full_path_in_server, "parameter can't be empty"

        res = None
        try:
            with open(full_path_to_file, mode="rb") as f:
                logging.info("Deploying...:  %s", full_path_in_server)

                res = requests.put(url= full_path_in_server, data=f)

                assert res.status_code in [200, 201, 202]
                logging.info("Success:  %s", full_path_in_server)

                return {"uploaded": file_to_upload }

        except Exception as ex:
            logging.expection("deploy_file faild") # so we'll have a nice print in the log

            # casue I don't know what print_error_exit() does, we'll call it.
            # even that I would prefer to just raise the expection up, i.e. "raise ex"
            print_error_exit ("Deployment to %s failed. status_code = %s, returned_text = %s" % 
                (full_path_in_server, res.status_code if res else None, res.text if res else None))

{% endhighlight %}

[1]: http://docs.python-requests.org/en/master/user/advanced/#streaming-uploads
