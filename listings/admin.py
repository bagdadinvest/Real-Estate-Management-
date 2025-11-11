from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Listing

class ListingAdmin(ImportExportModelAdmin):
	list_display = ('id' , 'title' , 'is_published' , 'price' , 'list_date' ,'realtor')
	list_display_links = ('id' , 'title')
	list_filter = ('realtor', 'city','state' )
	list_editable = ('is_published',)
	search_fields = ('title','description','address','city','state','zipcode','price')
	list_per_page = 15


# Register your models here.
admin.site.register(Listing , ListingAdmin)
