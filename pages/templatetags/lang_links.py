from django import template
from django.conf import settings
from django.utils.translation import get_language


register = template.Library()


def _strip_language_prefix(path, codes):
    if not path:
        return '/'
    parts = path.split('/', 2)
    if len(parts) > 1 and parts[1] in codes:
        remainder = '/' + (parts[2] if len(parts) > 2 else '')
        return remainder or '/'
    return path


@register.simple_tag(takes_context=True)
def get_language_links(context):
    """Return a list of languages with URLs for the same path under each language prefix."""
    request = context.get('request')
    if request is None:
        return []

    path = request.path or '/'
    codes = set(code for code, _name in getattr(settings, 'LANGUAGES', []))
    base_path = _strip_language_prefix(path, codes)
    if not base_path.startswith('/'):
        base_path = '/' + base_path

    links = []
    for code, name in getattr(settings, 'LANGUAGES', []):
        url = '/%s%s' % (code, base_path)
        links.append({'code': code, 'name': name, 'url': url})
    return links


@register.simple_tag
def get_current_language_code():
    return (get_language() or getattr(settings, 'LANGUAGE_CODE', 'en')).split('-')[0]
