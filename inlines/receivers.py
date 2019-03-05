from inlines.parser import ContentParser


def reset_inlines_cache(sender, instance, **kwargs):
    """
    Render any inlines in the object's content property, overwriting the
    previously cached rendering.
    """
    return ContentParser(instance.content, reset_cache=True).render()
