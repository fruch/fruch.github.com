---
layout: page
title: Welcome
tagline: Supporting tagline
---
{% include JB/setup %}

My first take on writing a blog, hope I don't bore anyone to death.
I hope you'll enjoy yourself...

## Latest blog posts
<ul class="posts">
{% for post in site.posts limit: 4 %}
<li>
    <span><a href="{{ post.url }}" class="blog-title">{{ post.title }}</a></span>
    <span style="float:right;"><em>posted on {{ post.date | date: '%B %d, %Y' }}</em></span>
</li>
{% endfor %}
</ul>
