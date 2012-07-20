django-inlineobjects
====================

A reusable [Django](http://www.djangoproject.com/) application used to insert objects into other objects. This application was originally created by [Nathan Borror](http://nathanborror.com/) for [django-basic-apps](https://github.com/nathanborror/django-basic-apps), his collection of simple prebuilt Django applications.


How it Works
------------

A template filter is created which renders inline markup to include content.


Requirements
------------

* [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/) is required for parsing markup.


Installation
------------

django-inlineobjects is available on PyPI and can be installed with PIP.

    pip install django-inlineobjects

Alternatively, you may download the source and install it.

    python setup.py install


Setup
-----

Add `inlines` to your `settings.INSTALLED_APPS`.


Usage
-----

To include a photo in a blog post body, you might put the following into the body.

    <inline type="media.photo" id="1" />

To render this in a template, you would use the template filter.

    {% load inlines_tags %}
    {{ post.body|render_inlines }}

This would insert the `media.photo` object with an ID of `1` into the post body.


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

How content is rendered is determined by a template. These templates should be stored within a template directory called `inlines` and use the filename structure `<app_name>_<model_name>.html`. The above usage example, for instance, would look for a template called `templates/media_photo.html`.

If the appropriate template for the object cannot be found, the `templates/default.html` template should be used instead.

Templates are not included with this application. They should be created by the user.
