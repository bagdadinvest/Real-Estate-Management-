from django import template
from html import unescape
import re

register = template.Library()


@register.filter
def font_href(value: str) -> str:
    """Normalize a font import value into a plain stylesheet href.

    Accepts any of the following and returns just the URL:
    - Direct URL: https://fonts.googleapis.com/...
    - CSS @import: @import url('https://fonts.googleapis.com/...');
    - HTML-entity encoded strings
    """
    if not value:
        return ""
    s = unescape(str(value)).strip().strip('"').strip("'")
    # If it's a full <link ... href="..."> tag, try to extract href
    m = re.search(r'href\s*=\s*([\"\'])(.*?)\1', s, flags=re.IGNORECASE)
    if m:
        return m.group(2).strip()
    # If it's an @import expression, extract the url(...)
    if '@import' in s:
        m = re.search(r'url\(\s*([\"\']?)([^\)\"\']+)\1\s*\)', s, flags=re.IGNORECASE)
        if m:
            return m.group(2).strip()
    # If it contains url(...), extract
    m = re.search(r'url\(\s*([\"\']?)([^\)\"\']+)\1\s*\)', s, flags=re.IGNORECASE)
    if m:
        return m.group(2).strip()
    return s

