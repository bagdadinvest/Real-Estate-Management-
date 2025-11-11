from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Post, Categories, PostComment

class PostAdmin(ImportExportModelAdmin):
    pass

class PostCommentAdmin(ImportExportModelAdmin):
    pass

class CategoriesAdmin(ImportExportModelAdmin):
    pass

# Register your models here.
admin.site.register(Post, PostAdmin)
admin.site.register(PostComment, PostCommentAdmin)
admin.site.register(Categories, CategoriesAdmin)
