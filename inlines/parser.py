from builtins import next, str, object
from bs4 import BeautifulSoup
from bs4.element import Tag
from django.apps import apps
from django.core.cache import cache
from django.db.models import Case, When
from django.template import TemplateSyntaxError
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from inlines import settings


class InlineRenderer(object):

    def __init__(self, inline):
        self.inline = inline
        if not isinstance(self.inline, Tag):
            raise ValueError('Inline must be bs4.element.Tag')
        self.get_app_model()
        self.get_lookup_key()
        self.get_lookup_value()
        self.build_context()
        self.build_cache_key()

    def get_app_model(self):
        # Look for inline type, 'app.model'
        self.app_label, self.model_name = self.inline['type'].split('.')
        return self.app_label, self.model_name

    def get_lookup_key(self):
        self.lookup_key = next((x for x in settings.INLINES_LOOKUP_KEYS if x in self.inline.attrs), None)
        if not self.lookup_key:
            raise ValueError('Failed to find any supported lookup key in tag: %s' % self.inline)
        return self.lookup_key

    def get_lookup_value(self):
        self.lookup_value = self.inline[self.lookup_key]
        # If the value contains a comma, treat it as a list of multiple
        # objects.
        if ',' in self.lookup_value:
            self.lookup_is_list = True
        else:
            self.lookup_is_list = False
        return self.lookup_value

    def build_cache_key(self):
        self.cache_key = 'inlines-%s-%s:%s' % (
            self.inline['type'],
            self.lookup_key,
            self.lookup_value,
        )
        return self.cache_key

    def get_model(self):
        self.model = apps.get_model(self.app_label, self.model_name)
        return self.model

    def build_context(self):
        # Create the context with all the attributes in the inline markup.
        self.context = self.inline.attrs.copy()
        return self.context

    def render_template(self):
        template = [
            "%s/inlines/%s.html" % (self.app_label, self.model_name),
            "inlines/%s_%s.html" % (self.app_label, self.model_name),
            "inlines/default.html",
        ]
        return render_to_string(template, self.context)

    def lookup_object_list(self):
        lookup_list = [x.strip() for x in self.lookup_value.split(',')]
        # Build a conditional to sort the objects, such that they are returned
        # in the same order that they were specified in the tag.
        ordering = Case(*[When(then=index, **{self.lookup_key: x}) for index, x in enumerate(lookup_list)])
        obj_list = self.model.objects.filter(
            **{'%s__in' % self.lookup_key: lookup_list}
        ).order_by(
            ordering
        )
        if not obj_list:
            raise ValueError(
                'Failed to find any objects for tag: %s' % self.inline
            )
        self.context['object_list'] = obj_list
        return obj_list

    def lookup_object(self):
        try:
            obj = self.model.objects.get(**{self.lookup_key: self.lookup_value})
        except self.model.DoesNotExist:
            raise ValueError(
                'Failed to find object for tag: %s' % self.inline
            )
        self.context['object'] = obj
        return obj

    def render(self):
        # Attempt to get the rendered template from the cache.
        if settings.INLINES_CACHE_TIMEOUT:
            rendered_template = cache.get(self.cache_key)
        # If that failed, get the objects and render the template normally.
        if not rendered_template:
            self.get_model()
            if self.lookup_is_list:
                self.lookup_object_list()
            else:
                self.lookup_object()
            rendered_template = self.render_template()
            # Store the rendered template in the cache.
            if settings.INLINES_CACHE_TIMEOUT:
                cache.set(
                    self.cache_key,
                    rendered_template,
                    settings.INLINES_CACHE_TIMEOUT,
                )
        return rendered_template


def inlines(value):
    content = BeautifulSoup(value, 'html.parser')
    content_string = str(content)
    for inline in content.findAll('inline'):
        try:
            rendered_inline = InlineRenderer(inline).render()
        except Exception as e:
            if settings.INLINES_DEBUG:
                raise TemplateSyntaxError('Failed to render inline: %s' % e.message)
            else:
                rendered_inline = ''
        content_string = content_string.replace(str(inline), rendered_inline)
    return mark_safe(content_string)
