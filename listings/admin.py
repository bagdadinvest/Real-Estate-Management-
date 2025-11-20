from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from django import forms
from import_export.admin import ImportExportModelAdmin
from .models import Listing, ListingImage

# Optional: django-image-uploader-widget integration (nice preview/replace UI)
try:
    from image_uploader_widget.widgets import ImageUploaderWidget  # type: ignore
    HAS_IMAGE_UPLOADER = True
except Exception:
    ImageUploaderWidget = None  # type: ignore
    HAS_IMAGE_UPLOADER = False


if HAS_IMAGE_UPLOADER:
    class ListingImageForm(forms.ModelForm):
        class Meta:
            model = ListingImage
            fields = '__all__'
            widgets = {
                'image': ImageUploaderWidget(),
            }
else:
    class ListingImageForm(forms.ModelForm):  # fallback default form
        class Meta:
            model = ListingImage
            fields = '__all__'

class ListingImageInline(admin.StackedInline):
    model = ListingImage
    extra = 0
    form = ListingImageForm
    fields = (
        'preview', 'image', 'title', 'order', 'is_primary', 'is_visible',
        ('crop_x', 'crop_y', 'crop_width', 'crop_height'),
    )
    readonly_fields = ('preview',)
    ordering = ('order', 'id')

    def preview(self, obj):
        if getattr(obj, 'image', None):
            try:
                return format_html('<img src="{}" style="max-width:160px; height:auto; border-radius:6px;"/>', obj.image.url)
            except Exception:
                return ""
        return ""
    preview.short_description = "Preview"


class ListingAdmin(ImportExportModelAdmin):
    list_display = (
        'id', 'title', 'is_published', 'price', 'list_date', 'realtor',
        'external_id', 'original_url_link'
    )
    list_display_links = ('id' , 'title')
    list_filter = ('realtor', 'city','state' )
    list_editable = ('is_published',)
    search_fields = (
        'title','description','address','city','state','zipcode','price',
        'external_id','original_url'
    )
    list_per_page = 15
    inlines = [ListingImageInline]

    def original_url_link(self, obj):
        url = getattr(obj, 'original_url', '') or ''
        if not url:
            return ''
        try:
            return format_html('<a href="{}" target="_blank" rel="noopener noreferrer">Source</a>', url)
        except Exception:
            return url
    original_url_link.short_description = 'Original URL'


# Register your models here.
admin.site.register(Listing , ListingAdmin)
