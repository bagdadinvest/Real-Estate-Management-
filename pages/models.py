from django.db import models


class ThemeSettings(models.Model):
    """Site-wide theme settings editable in admin.

    Keep as a single-row table; use pk=1.
    """
    primary_color = models.CharField(max_length=16, default="#c3476c")
    accent_color = models.CharField(max_length=16, default="#0071f8")
    background_color = models.CharField(max_length=16, default="#ffffff")
    text_color = models.CharField(max_length=16, default="#1e1e1e")
    font_family = models.CharField(max_length=200, default="Titillium Web, sans-serif")
    font_import_url = models.CharField(max_length=300, blank=True, default="", help_text="Full Google Fonts <link> href or CSS @import URL")
    font_selectors = models.CharField(max_length=300, default="html, body", help_text="CSS selectors to apply the font-family to")
    custom_css = models.TextField(blank=True, default="", help_text="Additional CSS overrides injected after theme variables")

    class Meta:
        verbose_name = "Theme Settings"
        verbose_name_plural = "Theme Settings"

    def __str__(self) -> str:
        return "Theme Settings"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
