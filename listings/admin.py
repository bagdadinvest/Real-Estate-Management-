from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from django import forms
from import_export.admin import ImportExportModelAdmin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.management import call_command
from .models import Listing, ListingImage, ListingImportJob
from .importer import start_import_job_async

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
    preview.short_description = _("Preview")


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
            return format_html('<a href="{}" target="_blank" rel="noopener noreferrer">{}</a>', url, _("Source"))
        except Exception:
            return url
    original_url_link.short_description = _('Original URL')


# Register your models here.
admin.site.register(Listing , ListingAdmin)


class ListingImportJobForm(forms.ModelForm):
    class Meta:
        model = ListingImportJob
        fields = '__all__'

    def clean(self):
        cleaned = super().clean()
        single_url = (cleaned.get('single_url') or '').strip()
        csv_file = cleaned.get('csv_file')
        if not single_url and not csv_file:
            raise forms.ValidationError(_('Provide either a single URL or upload a CSV file.'))
        return cleaned


@admin.register(ListingImportJob)
class ListingImportJobAdmin(admin.ModelAdmin):
    form = ListingImportJobForm
    list_display = (
        'id', 'realtor', 'created_by', 'status', 'created_at', 'started_at', 'finished_at'
    )
    list_filter = ('status', 'realtor')
    search_fields = ('id', 'realtor__name', 'created_by__username', 'single_url')
    readonly_fields = (
        'status', 'log', 'created_at', 'started_at', 'finished_at', 'created_by', 'effective_csv_path'
    )
    fieldsets = (
        (_("Source"), {
            'fields': ('realtor', 'single_url', 'csv_file', 'cookie_file')
        }),
        (_("Options"), {
            'fields': ('delay', 'debug', 'skip_geocode', 'headed', 'images_max', 'no_images')
        }),
        (_("Execution"), {
            'fields': ('status', 'effective_csv_path', 'created_by', 'created_at', 'started_at', 'finished_at', 'log')
        }),
    )

    def effective_csv_path(self, obj):
        return getattr(obj, 'csv_path_cached', '') or ''
    effective_csv_path.short_description = _('CSV path used')

    def save_model(self, request, obj, form, change):
        is_new = obj.pk is None
        if is_new and not getattr(obj, 'created_by_id', None):
            obj.created_by = request.user
        # Reset execution fields on every save if pending
        if is_new:
            obj.status = 'pending'
            obj.log = ''
            obj.started_at = None
            obj.finished_at = None
        super().save_model(request, obj, form, change)

        # Kick off async run when created
        if is_new:
            try:
                start_import_job_async(obj.id)
                self.message_user(request, _("Import job started."), level=messages.INFO)
            except Exception as e:
                self.message_user(request, _("Failed to start job: %s") % e, level=messages.ERROR)
