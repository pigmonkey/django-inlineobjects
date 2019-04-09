# django-inlineobjects

A reusable [Django](http://www.djangoproject.com/) application used to render objects within strings. This application was originally created by [Nathan Borror](http://nathanborror.com/) for [django-basic-apps](https://github.com/nathanborror/django-basic-apps), his collection of simple prebuilt Django applications.


## Requirements

* [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/) is required for parsing markup.


## Installation

django-inlineobjects is available on PyPI and can be installed with PIP.

    pip install django-inlineobjects

Alternatively, you may download the source and install it.

    python setup.py install


## Usage

To include a photo in a blog post body, you might put the following into the body field:

    <inline type="media.photo" id="1"></inline>

To render this in a template, you would use the template filter.

    {% load inlines_tags %}
    {{ post.body|render_inlines }}

This would insert the `Photo` object with an ID of `1` from the app `media` into the post body.


### Multiple Objects

To render multiple objects of the same type, you could use multiple tags:

    <inline type="media.photo" id="1"></inline>
    <inline type="media.photo" id="2"></inline>
    <inline type="media.photo" id="3"></inline>

Or you could achieve the same list by using a single tag with a comma separated list of identifiers.

    <inline type="media.photo" id="1,2,3"></inline>


### Admin

A javascript-based interface to add inlines can be added to the Django admin site using the included template. The included template must be added to the relevant model's change form.

For example, to add the interface to the `body` field of the `Post` model in an application called `blog`, you would create the template `admin/blog/post/change_form.html`. The content of that template would contain the following:

    {% extends "admin/change_form.html" %}

    {% block extrahead %}
        {{ block.super }}
        {% include 'inlines/inlines.js' with field='post' %}
    {% endblock %}

This template expands the default `admin/change_form.html` template, including `inlines/inlines.js` in the `extrahead` block. The included template expects the variable `field` to be included in the context. The variable should be set to the name of the model field that you want the inlines to be applied to.


### Templates

How content is rendered is determined by a template. The renderer will look for the following template names:

    <app_name>/inlines/<model>.html
    inlines/<app_name>_<model>.html
    inlines/default.html

Given the previous inline tag example with `type="media.photo"`, the preferred template path would be `media/inlines/photo.html`.

A template name suffix may also be specified in the inline tag. This can be done either with a `template_name_suffix` attribute or, to save keystrokes, a `template` suffix. The following two tags are equivalent:

    <inline type="media.photo" id="1" template_name_suffix="banner"></inline>
    <inline type="media.photo" id="1" template_suffix="banner"></inline>

Both will result in the parser looking for the following template paths:

    media/inlines/photo_banner.html
    inlines/media_photo_banner.html
    inlines/default.html


### Context

In addition to the specified object, each attribute of the inline tag is passed to the template context.

This allows you to support arbitrary attributes, such as class names:

    <inline type="media.photo" id="1" class="right"></inline>

Which can then be accessed in your template:

    <img src="{{ object.url }}" alt="{{ object.name }}" {% if class %}class="{{ class|join:" " }}{% endif %}>


## Setup

Add `inlines` to your `settings.INSTALLED_APPS`.


## Settings

### `INLINES_LOOKUP_KEYS`

Default: `['id']`

Provide a list of attribute keys which should be used to lookup objects. For example, if you want to be able to reference objects by their ID or their slug, you would set `INLINES_LOOKUP_KEYS = ['id', 'slug']`.

### `INLINES_DEBUG`

Default: `settings.DEBUG`

When debug is disabled, the renderer will fail silently if it encounters any errors. The inline tag will simply be replaced by an empty string in the output. When debug is enabled, relevant errors will be raised.

### `INLINES_CACHE_TIMEOUT`

Default: `0`

When set to a positive integer, this will cause the rendered to be cached for the given amount of seconds.

Note that the cache key is unique to the inline tag. If you allow lookups by `id` and `slug`, and refer to an object by its `id` in one tag and its `slug` in another tag, this will result in two seperate cache entries, despite the rendered template being identical for both:

    <inline type="media.photo" id="1"></inline>
    <inline type="media.photo" slug="foo-bar"></inline>

### `INLINES_ALLOWED_TYPES`

Default: `None`

By default the renderer will attempt to lookup any object given in the `type` attribute of the inline tag. If you wish to only support certain objects, you may whitelist them here. Doing this will prevent querying the database for objects for which you do not have inline templates.

### `INLINES_MANAGERS`

Default: `None`

If you have a custom manager you wish to always be used when querying objects of a certain type, you may define it as a dictionary here.

For instance, perhaps you use inlines to include photos. Your photos may go through some approval process before they are allowed to be displayed publicly. You have a `published()` manager which include filters to only return published photos. If you never want to allow unpublished photos to be rendered as inlines, you could set this option to:

    INLINES_MANAGERS = {
        'media.photo': 'published',
    }

When the renderer is querying photos with this configuration, it will only use `Photo.objects.published().filter(...)`.
