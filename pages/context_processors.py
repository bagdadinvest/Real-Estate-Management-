from .models import ThemeSettings


def theme_settings(request):
    """Inject theme settings into all templates as `theme`."""
    try:
        theme = ThemeSettings.get_solo()
    except Exception:
        theme = None
    return {"theme": theme}

