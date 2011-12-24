django-inlines
============

A reusable [Django](http://www.djangoproject.com/) application used to insert content objects into other pieces of content. This application was originally created by [Nathan Borror](http://nathanborror.com/) for [django-basic-apps](https://github.com/nathanborror/django-basic-apps), his collection of simple prebuilt Django applications.


How it Works
------------

A template filter is created which renders inline markup to include content.

Setup
-----

Add `inlines` to your `settings.INSTALLED_APPS`.


Usage
-----

To include a photo in a blog post body, you might put the following into the body.

    <inline type="media.photo" id="1" />

To render this in a template, you would use the template filter.

    {% load inlines %}
    {{ post.body|render_inlines }}

This would insert the `media.photo` object with an ID of `1` into the post body.


### Templates

How content is rendered is determined by a template. These templates should be stored within a template directory called `inlines` and use the filename structure `<app_name>_<model_name>.html`. The above usage example, for instance, would look for a template called `templates/media_photo.html`.

If the appropriate template for the object cannot be found, the `templates/default.html` template should be used instead.

Templates are not included with this application. They should be created by the user.
