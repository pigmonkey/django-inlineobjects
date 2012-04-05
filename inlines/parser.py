from django.template import TemplateSyntaxError
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.utils.encoding import smart_unicode
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


def inlines(value, return_list=False):
    try:
        from BeautifulSoup import BeautifulStoneSoup
    except ImportError:
        from beautifulsoup import BeautifulStoneSoup

    content = BeautifulStoneSoup(value, selfClosingTags=['inline', 'img', 'br',
                                                         'input', 'meta',
                                                         'link', 'hr'])

    # Return a list of inline objects found in the value.
    if return_list:
        inline_list = []
        for inline in content.findAll('inline'):
            rendered_inline = render_inline(inline)
            inline_list.append(rendered_inline['context'])
        return inline_list

    # Replace inline markup in the value with rendered inline templates.
    else:
        for inline in content.findAll('inline'):
            rendered_inline = render_inline(inline)
            if rendered_inline:
                inline_template = render_to_string(rendered_inline['template'],
                                                   rendered_inline['context'])
            else:
                inline_template = ''
            value = value.replace(str(inline), inline_template)
        return mark_safe(unicode(value))


def render_inline(inline):
    """
    Replace inline markup with template markup that matches the
    appropriate app and model.
    """

    # Look for inline type, 'app.model'
    try:
        app_label, model_name = inline['type'].split('.')
    except:
        if settings.DEBUG:
            raise TemplateSyntaxError("Couldn't find the attribute 'type' in "
                                       "the <inline> tag.")
        else:
            return ''

    # Look for content type
    try:
        content_type = ContentType.objects.get(app_label=app_label,
                                               model=model_name)
        model = content_type.model_class()
    except ContentType.DoesNotExist:
        if settings.DEBUG:
            raise TemplateSyntaxError("Inline ContentType not found.")
        else:
            return ''

    # Create the context with all the attributes in the inline markup.
    context = {k: v for k, v in inline.attrs}

    # If multiple IDs were specified, build a list of all requested objects
    # and add them to the context.
    try:
        try:
            id_list = [int(i) for i in inline['ids'].split(',')]
            obj_list = model.objects.in_bulk(id_list)
            obj_list = list(obj_list[int(i)] for i in id_list)
            context['object_list'] = obj_list
        except ValueError:
            if settings.DEBUG:
                raise ValueError("The <inline> ids attribute is missing or "
                                 "invalid.")
            else:
                return ''

    # If only one ID was specified, retrieve the requested object and add it
    # to the context.
    except KeyError:
        try:
            obj = model.objects.get(pk=inline['id'])
            context['object'] = obj
        except model.DoesNotExist:
            if settings.DEBUG:
                raise model.DoesNotExist("%s with pk of '%s' does not exist"
                                         % (model_name, inline['id']))
            else:
                return ''
        except:
            if settings.DEBUG:
                raise TemplateSyntaxError("The <inline> id attribute is "
                                          "missing or invalid.")
            else:
                return ''

    # Set the name of the template that should be used to render the inline.
    template = ["inlines/%s_%s.html" % (app_label, model_name),
                "inlines/default.html"]

    # Return the template name and the context.
    return {'template': template, 'context': context}
