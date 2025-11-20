from django.contrib import admin
from .models import ThemeSettings


@admin.register(ThemeSettings)
class ThemeSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'primary_color', 'accent_color', 'background_color', 'text_color',
                'font_family', 'font_import_url', 'font_selectors', 'custom_css'
            )
        }),
    )
    list_display = (
        'primary_color', 'accent_color', 'background_color', 'text_color',
        'font_family', 'font_import_url'
    )
    def has_add_permission(self, request):  # enforce single row
        return not ThemeSettings.objects.exists()

# Register your models here.
