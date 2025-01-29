import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ABRMS.settings')
django.setup()

from abrmservices.models import Listing

def retrieve_listing_photos(listing_id):
    try:
        # Retrieve the listing
        listing = Listing.objects.get(id=listing_id)
        
        # Retrieve related photos
        bathroom_photos = listing.bathroom_photos.all()
        toilet_photos = listing.toilet_photos.all()
        additional_photos = listing.additional_photos.all()

        # Print listing details
        print(f"Listing ID: {listing.id}")
        print(f"Listing Title: {listing.title}")

        # Print bathroom photos
        print("\nBathroom Photos:")
        for photo in bathroom_photos:
            print(f" - Photo ID: {photo.id}, URL: {photo.image.url}")

        # Print toilet photos
        print("\nToilet Photos:")
        for photo in toilet_photos:
            print(f" - Photo ID: {photo.id}, URL: {photo.image.url}")

        # Print additional photos
        print("\nAdditional Photos:")
        for photo in additional_photos:
            print(f" - Photo ID: {photo.id}, URL: {photo.image.url}")

    except Listing.DoesNotExist:
        print(f"No listing found with ID {listing_id}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Replace with the actual listing ID you want to retrieve
    listing_id = input("Enter the Listing ID: ")
    if listing_id.isdigit():
        retrieve_listing_photos(int(listing_id))
    else:
        print("Invalid ID. Please enter a numeric value.")

# listing = Listing.objects.get(id=15)
# print(listing.bathroom_photos.all())  # Should show queryset of photos
# print(listing.toilet_photos.all())
# print(listing.additional_photos.all())