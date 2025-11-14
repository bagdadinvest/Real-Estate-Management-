"""btre URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.views.decorators.clickjacking import xframe_options_exempt
from listings import views as listing_views
from graphene_django.views import GraphQLView
from blog.schema import schema
from pages import views as pages_views
from django.conf.urls.i18n import i18n_patterns


from django.conf.urls.static import static
from django.conf import settings

# Make Rosetta optional so URLs don't break if not installed
try:
    import rosetta  # noqa: F401
    _has_rosetta = True
except Exception:
    _has_rosetta = False

# Include django-distill URL patterns (static site generation)
from coralcity import distill_urls as distill

urlpatterns = [
    path('admin/', admin.site.urls),
    # The 'i18n/' path is where Django handles setting the language and should usually not be prefixed.
    path('i18n/', include('django.conf.urls.i18n')), 
    path('graphql/', GraphQLView.as_view(graphiql=True)), # You might keep this non-prefixed or put it inside i18n_patterns if you need translated GraphQL endpoints. Keeping outside for this example.
]

if _has_rosetta:
    urlpatterns += [path('rosetta/', include('rosetta.urls'))]

# Prefixed URLs (All user-facing paths)
# All paths within i18n_patterns will automatically have the language prefix (e.g., /en/ or /es/)
# prepended to them.
prefixed_urlpatterns = i18n_patterns(
    path('', include('pages.urls')),
    path('listings/', include('listings.urls')),
    path('accounts/', include('accounts.urls')),
    path('contacts/', include('contacts.urls')),
    path('AgesVerification/', include('Ages.urls')),
    path('blog/', include('blog.urls')),
    # New frontend demo routes
    path('new/', TemplateView.as_view(template_name='newfrontend/index.html'), name='new_index'),
    path('new/properties/', listing_views.new_properties, name='new_properties'),
    path('new/financing/', pages_views.financing, name='new_financing'),
    path('new/property-details/', TemplateView.as_view(template_name='newfrontend/property-details.html'), name='new_property_details'),
    path('new/listing/<int:listing_id>/', listing_views.new_listing_detail, name='new_listing_detail'),
    path('new/contact/', TemplateView.as_view(template_name='newfrontend/contact.html'), name='new_contact'),
    path('new/map/', listing_views.new_map_view, name='new_map'),
    path('new/map-copy/', listing_views.new_map_view_copy, name='new_map_copy'),
    path('new/map-simplified/', xframe_options_exempt(TemplateView.as_view(template_name='newfrontend/mapstandalone/simplified/index.html')), name='new_map_simplified'),
    # 404 preview route so you can check the page without toggling DEBUG
    path('new/404-preview/', TemplateView.as_view(template_name='newfrontend/page-404.html'), name='new_404_preview'),
    # Include distill URL patterns so static generation covers all languages
    *distill.urlpatterns,
)

# Combine non-prefixed and prefixed URLs
urlpatterns += prefixed_urlpatterns

# Static and Debug Toolbar URLs remain outside i18n_patterns
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

# Distill URL patterns are included inside i18n_patterns above for per-language output

# Django Debug Toolbar (only if installed and debug)
if settings.DEBUG and 'debug_toolbar' in settings.INSTALLED_APPS:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

# Custom error handlers
handler404 = 'pages.views.custom_404'
