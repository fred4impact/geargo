from django import template

register = template.Library()


@register.filter(name='length_is')
def length_is(value, arg):
    """
    Check if the length of a value equals the given argument.
    Usage: {{ value|length_is:5 }}
    Returns True if len(value) == arg, False otherwise.
    """
    try:
        if value is None:
            return False
        length = len(value)
        arg = int(arg)
        return length == arg
    except (TypeError, ValueError):
        return False
