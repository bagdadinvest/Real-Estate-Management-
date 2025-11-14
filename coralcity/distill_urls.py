from django_distill import distill_path
from django.views.generic import TemplateView
from listings import views as listing_views
from pages import views as pages_views
from listings.models import Listing

def get_all_listing_ids():
    # Return a list of dictionaries, one for each listing
    # The key, 'listing_id', matches the name of the parameter in the URL
    return [{'listing_id': listing.id} for listing in Listing.objects.filter(is_published=True)]

# The list of URLs to distill
urlpatterns = [
    distill_path('new/',
                 TemplateView.as_view(template_name='newfrontend/index.html'),
                 name='new_index'),
    distill_path('new/properties/',
                 listing_views.new_properties,
                 name='new_properties'),
    distill_path('new/financing/',
                 pages_views.financing,
                 name='new_financing'),
    distill_path('new/property-details/',
                 TemplateView.as_view(template_name='newfrontend/property-details.html'),
                 name='new_property_details'),
    distill_path('new/listing/<int:listing_id>/',
                 listing_views.new_listing_detail,
                 name='new_listing_detail',
                 distill_func=get_all_listing_ids),
    distill_path('new/contact/',
                 TemplateView.as_view(template_name='newfrontend/contact.html'),
                 name='new_contact'),
    distill_path('new/map/',
                 listing_views.new_map_view,
                 name='new_map'),
    distill_path('new/404-preview/',
                 TemplateView.as_view(template_name='newfrontend/page-404.html'),
                 name='new_404_preview'),
]
