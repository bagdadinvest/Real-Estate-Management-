from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse, JsonResponse
from django.conf import settings

from listings.choices import price_choices , bedroom_choices , state_choices, type_choices

from .models import Listing

# Create your views here
def index(request):
	listings = Listing.objects.all().order_by('-list_date').filter(is_published=True)
	paginator = Paginator(listings, 6)
	page = request.GET.get('page')
	paged_listings = paginator.get_page(page)
	return render(request,'listings/listings.html',{'listings' : paged_listings})


def new_properties(request, page=None):
    """Render the new frontend properties page with the same listings data/pagination."""
    listings = Listing.objects.all().order_by('-list_date').filter(is_published=True)
    paginator = Paginator(listings, 6)
    # Accept page from path or querystring for flexibility (works in static and dynamic)
    # Resolve page number robustly (tolerate None/invalid/zero)
    raw = page if page is not None else request.GET.get('page')
    try:
        page_num = int(raw) if raw is not None else 1
    except (TypeError, ValueError):
        page_num = 1
    if page_num < 1:
        page_num = 1
    paged_listings = paginator.get_page(page_num)
    return render(request, 'newfrontend/properties.html', {'listings': paged_listings})


def new_listing_detail(request, listing_id):
	listing = get_object_or_404(Listing, pk=listing_id)
	return render(request, 'newfrontend/property-details.html', {'listing': listing})


def new_property_details_preview(request):
    """Preview page for new property details without specifying an ID.

    - If there is a published listing, render that.
    - Otherwise, render a lightweight demo listing so templates don't fail.
    This supports static builds (django-distill) where a fixed route exists.
    """
    listing = Listing.objects.filter(is_published=True).order_by('-list_date').first()
    if not listing:
        # Build a simple stand-in object with the attributes used by the template
        from types import SimpleNamespace
        listing = SimpleNamespace(
            id=0,
            title="Sample Property",
            address="123 Demo Street",
            description="Demo property for preview.",
            deal_type="rent",
            property_type=" Apartment",
            city="Istanbul",
            state="TR",
            price=0,
            bedrooms=0,
            bathrooms=0,
            m2_gross=None,
            m2_net=None,
            rooms_text="",
            building_age=None,
            floor_number=None,
            floors_total=None,
            heating="",
            kitchen_type="",
            balcony="",
            parking_area="",
            usage_status="",
            in_complex=None,
            complex_name="",
            elevator=None,
            furnished=None,
            maintenance_fee=None,
            deposit=None,
            deed_status="",
            from_whom="",
            external_id=None,
            ad_date=None,
            list_date=None,
            visible_images=[],
        )
    return render(request, 'newfrontend/property-details.html', {'listing': listing})


def listing(request , listing_id):
	listing = get_object_or_404(Listing , pk=listing_id)
	context = {
	  'listing' : listing
	}
	return render(request,'listings/listing.html',context)


def search(request):
	queryset_list = Listing.objects.order_by('-list_date')
	if 'keywords' in request.GET:
		keywords = request.GET['keywords']
		if keywords:
			queryset_list = queryset_list.filter(description__icontains=keywords)

	if 'city' in request.GET:
		city = request.GET['city']
		if city:
			queryset_list = queryset_list.filter(city__iexact=city)

	if 'state' in request.GET:
		state = request.GET['state']
		if state:
			queryset_list = queryset_list.filter(state__iexact=state)

	if 'bedrooms' in request.GET:
		bedrooms = request.GET['bedrooms']
		if bedrooms:
			queryset_list = queryset_list.filter(bedrooms__lte=bedrooms)

	if 'price' in request.GET:
		price = request.GET['price']
		if price:
			queryset_list = queryset_list.filter(price__lte=price)


	return render(request,'listings/search.html',{
		'listings' : queryset_list,
        'state_choices' : state_choices,
        'bedroom_choices' : bedroom_choices,
        'price_choices' : price_choices,
        'type_choices' : type_choices,
        'values': request.GET,
		})


def map_view(request):
    return render(request, 'listings/map.html')


def map_data(request):
    # Get initial queryset and check total count
    qs = Listing.objects.filter(is_published=True)
    initial_count = qs.count()
    print(f"Initial published listings count: {initial_count}")

    # Check how many have coordinates
    has_coords = qs.exclude(latitude__isnull=True).exclude(longitude__isnull=True).count()
    print(f"Listings with coordinates: {has_coords}")

    # Print a sample of listings to check coordinate values
    sample = qs[:5]
    print("\nSample listings:")
    for listing in sample:
        print(f"ID: {listing.id}, Title: {listing.title}, Lat: {listing.latitude}, Lng: {listing.longitude}")

    # Optional filters to mirror search behavior
    keywords = request.GET.get('keywords')
    if keywords:
        qs = qs.filter(description__icontains=keywords)

    city = request.GET.get('city')
    if city:
        qs = qs.filter(city__iexact=city)

    state = request.GET.get('state')
    if state:
        qs = qs.filter(state__iexact=state)

    bedrooms = request.GET.get('bedrooms')
    if bedrooms:
        qs = qs.filter(bedrooms__lte=bedrooms)

    price = request.GET.get('price')
    if price:
        qs = qs.filter(price__lte=price)

    # Filter for listings with coordinates
    qs = qs.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    final_count = qs.count()
    print(f"\nFinal filtered listings count: {final_count}")

    features = []
    for obj in qs:
        properties = {
            "id": obj.id,
            "title": obj.title,
            "price": obj.price,
            "bedrooms": obj.bedrooms,
            "bathrooms": obj.bathrooms,
            "city": obj.city,
            "state": obj.state,
            "address": obj.address,
            "url": f"/listings/{obj.id}/",
        }
        # Collect available photos for swipeable gallery in popup from related images
        photos = []
        try:
            for img in obj.images.order_by('order', 'id'):
                if getattr(img, 'image', None):
                    photos.append(img.image.url)
        except Exception:
            pass
        if photos:
            properties["photos"] = photos
            # Keep legacy single photo key for backward-compat
            properties["photo_url"] = photos[0]

        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [obj.longitude, obj.latitude],
            },
            "properties": properties,
        })

    return JsonResponse({
        "type": "FeatureCollection",
        "features": features,
    })


def new_map_view(request):
	"""Render the new frontend map page."""
	return render(request, 'newfrontend/map.html')


def new_map_view_copy(request):
	"""Render the duplicate new frontend map page."""
	return render(request, 'newfrontend/map_copy.html')
