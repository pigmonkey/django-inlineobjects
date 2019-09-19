import hashlib

from builtins import next, str, object

from bs4 import BeautifulSoup
from bs4.element import Tag
from django.apps import apps
from django.core.cache import cache
from django.db.models import Case, When
from django.template import TemplateSyntaxError
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from inlines import settings


class InlineRenderer(object):

    def __init__(self, inline, reset_cache=False):
        self.inline = inline
        self.reset_cache = reset_cache
        self.clean()
        self.get_app_model()
        self.get_lookup_key()
        self.get_lookup_value()
        self.get_template_name_suffix()
        self.build_context()
        self.build_cache_key()

    def clean(self):
        if not isinstance(self.inline, Tag):
            raise ValueError('Inline must be bs4.element.Tag')
        if settings.INLINES_ALLOWED_TYPES and self.inline['type'] not in settings.INLINES_ALLOWED_TYPES:
            raise ValueError('Inline tag does not have an allowed type: %s' % self.inline)

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

    def get_template_name_suffix(self):
        self.template_name_suffix = ''
        self.template_key = next((x for x in ['template', 'template_name_suffix'] if x in self.inline.attrs), None)
        if self.template_key:
            self.template_name_suffix = '_%s' % self.inline[self.template_key]
        return self.template_name_suffix

    def build_cache_key(self):
        self.cache_key_string = 'inlines:%s' % str(self.inline.attrs)
        self.cache_key = hashlib.md5(self.cache_key_string.encode('utf-8')).hexdigest()
        return self.cache_key

    def get_model(self):
        self.model = apps.get_model(self.app_label, self.model_name)
        return self.model

    def get_manager(self):
        self.manager_name = 'all'
        if settings.INLINES_MANAGERS and self.inline['type'] in settings.INLINES_MANAGERS:
            self.manager_name = settings.INLINES_MANAGERS[self.inline['type']]
        self.manager = getattr(self.model.objects, self.manager_name)
        return self.manager

    def build_context(self):
        # Create the context with all the attributes in the inline markup.
        self.context = self.inline.attrs.copy()
        return self.context

    def render_template(self):
        template = [
            "%s/inlines/%s%s.html" % (self.app_label, self.model_name, self.template_name_suffix),
            "inlines/%s_%s%s.html" % (self.app_label, self.model_name, self.template_name_suffix),
            "inlines/default.html",
        ]
        return render_to_string(template, self.context)

    def lookup_object_list(self):
        lookup_list = [x.strip() for x in self.lookup_value.split(',')]
        # Build a conditional to sort the objects, such that they are returned
        # in the same order that they were specified in the tag.
        ordering = Case(*[When(then=index, **{self.lookup_key: x}) for index, x in enumerate(lookup_list)])
        obj_list = self.manager().filter(
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
            obj = self.manager().get(**{self.lookup_key: self.lookup_value})
        except self.model.DoesNotExist:
            raise ValueError(
                'Failed to find object for tag: %s' % self.inline
            )
        self.context['object'] = obj
        return obj

    def render(self):
        rendered_template = None
        # Attempt to get the rendered template from the cache.
        if not self.reset_cache and settings.INLINES_CACHE_TIMEOUT > 0:
            rendered_template = cache.get(self.cache_key)
        # If that failed, get the objects and render the template normally.
        if not rendered_template:
            self.get_model()
            self.get_manager()
            if self.lookup_is_list:
                self.lookup_object_list()
            else:
                self.lookup_object()
            rendered_template = self.render_template()
            # Store the rendered template in the cache.
            if settings.INLINES_CACHE_TIMEOUT > 0:
                cache.set(
                    self.cache_key,
                    rendered_template,
                    settings.INLINES_CACHE_TIMEOUT,
                )
        return rendered_template


class ContentParser(object):

    def __init__(self, content, reset_cache=False):
        self.content = content
        self.reset_cache = reset_cache
        self.soup = BeautifulSoup(self.content, 'html.parser')
        self.soup_string = str(self.soup)
        self.find_inlines()

    def find_inlines(self):
        self.inlines = self.soup.find_all('inline')
        return self.inlines

    def render(self):
        for inline in self.inlines:
            try:
                rendered_inline = InlineRenderer(inline, self.reset_cache).render()
            except Exception as e:
                if settings.INLINES_DEBUG:
                    raise TemplateSyntaxError('Failed to render inline: %s' % e)
                else:
                    rendered_inline = ''
            self.soup_string = self.soup_string.replace(str(inline), rendered_inline)
        return mark_safe(self.soup_string)
