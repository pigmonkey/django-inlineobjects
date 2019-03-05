from bs4 import BeautifulSoup
from django.template import TemplateSyntaxError
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from inlines import settings


def inlines(value):
    content = BeautifulSoup(value, 'html.parser')
    content_string = str(content)
    for inline in content.findAll('inline'):
        rendered_inline = render_inline(inline)
        content_string = content_string.replace(str(inline), rendered_inline)
    return mark_safe(content_string)


def render_inline(inline):
    """
    Replace inline markup with template markup that matches the appropriate app
    and model.
    """

    # Look for inline type, 'app.model'
    try:
        app_label, model_name = inline['type'].split('.')
    except:
        if settings.INLINES_DEBUG:
            raise TemplateSyntaxError(
                "Couldn't find the attribute 'type' in the <inline> tag."
            )
        else:
            return ''

    # Find the first specified lookup key.
    lookup_key = next((x for x in settings.INLINES_LOOKUP_KEYS if x in inline.attrs), None)
    if not lookup_key:
        if settings.INLINES_DEBUG:
            raise TemplateSyntaxError(
                "Couldn't find any supported lookup key in the <inline> tag."
            )
        else:
            return ''

    # Look for content type
    try:
        content_type = ContentType.objects.get(
            app_label=app_label,
            model=model_name,
        )
        model = content_type.model_class()
    except ContentType.DoesNotExist:
        if settings.INLINES_DEBUG:
            raise TemplateSyntaxError("Inline ContentType not found.")
        else:
            return ''

    # Create the context with all the attributes in the inline markup.
    context = dict((attr[0], attr[1]) for attr in inline.attrs)

    lookup_value = inline[lookup_key]
    # If multiple lookups were specified, build a list of all requested objects
    # and add them to the context.
    if ',' in lookup_value:
        lookup_list = [x.strip() for x in lookup_value.split(',')]
        obj_list = model.objects.filter(**{'%s__in' % lookup_key: lookup_list})
        if not obj_list:
            if settings.INLINES_DEBUG:
                raise model.DoesNotExist(
                    "Failed to find any %s with %s of '%s'" % (
                        model_name,
                        lookup_key,
                        lookup_list,
                    )
                )
            else:
                return ''
        else:
            context['object_list'] = obj_list
    # If only one lookup was specified, retrieve the requested object and add
    # it to the context.
    else:
        try:
            obj = model.objects.get(**{lookup_key: lookup_value})
        except model.DoesNotExist:
            if settings.INLINES_DEBUG:
                raise model.DoesNotExist(
                    "%s with %s of '%s' does not exist" % (
                        model_name,
                        lookup_key,
                        lookup_value,
                    )
                )
            else:
                return ''
        else:
            context['object'] = obj

    # Set the name of the template that should be used to render the inline.
    template = [
        "%s/inlines/%s.html" % (app_label, model_name),
        "inlines/%s_%s.html" % (app_label, model_name),
        "inlines/default.html",
    ]

    # Returned the rendered template.
    return render_to_string(template, context)
