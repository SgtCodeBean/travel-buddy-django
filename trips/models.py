# trips/models.py
from django.db import models
from django.contrib.auth.models import User

# Django model representing saved itineraries in the database
class Itinerary(models.Model):
    # Choices for visibility field
    VISIBILITY_CHOICES = (
        ('public', 'Public'),
        ('private', 'Private'),
    )

    # Name of the itinerary
    name = models.CharField(max_length=200, default="My Itinerary")

    # Foreign key to Django's built-in User model
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Destination name(s)
    destination = models.CharField(max_length=200)

    # Duration of the trip in days
    duration = models.PositiveIntegerField(help_text="Duration in days", default=0)

    # Budget for the trip
    budget = models.DecimalField(max_digits=10, decimal_places=2)

    # Star rating (optional)
    star_rating = models.CharField(max_length=10, blank=True)

    # Number of reviews
    review_count = models.PositiveIntegerField(blank=True, default=0)

    # Visibility setting: 'public' or 'private'
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default="public")

    start_date = models.DateField(blank=True, null=True, help_text="Optional start date of the itinerary")
    end_date = models.DateField(blank=True, null=True, help_text="Optional end date of the itinerary")

    # String representation for Django admin or debugging
    def __str__(self):
        return self.name

# Mock class used for loading hardcoded itinerary data (not tied to database)
class ItineraryDetails:
    def __init__(self, id, name, user, destination, duration, budget, star_rating, review_count, visibility, details):
        self.id = id
        self.name = name
        self.user = user
        self.destination = destination
        self.duration = duration
        self.budget = budget
        self.star_rating = star_rating
        self.review_count = review_count
        self.visibility = visibility
        self.details = details

        @property
        def get_duration(self):
            if self.start_date and self.end_date:
                return (self.end_date - self.start_date).days
            return None

# HTML string representing detailed itinerary content for Europe trip
itinerary_details_html = """
<h2>Backpacking Through Europe ✈️</h2>
<h3><span class="stars">⭐⭐⭐☆☆</span></h3>
<div class="itinerary-box">
    <!-- Day 1 -->
    <h3>📅 Day 1: <a href="#">Barcelona, Spain 🇪🇸</a></h3>
    <ul>
        <li><strong>Morning:</strong> Arrive in Barcelona and check into a hostel like <a href="#">Hostel One Ramblas</a>.</li>
        <li><strong>Midday:</strong> Visit <a href="#">La Sagrada Familia</a> and <a href="#">Gothic Quarter</a>.</li>
        <li><strong>Lunch:</strong> Try <a href="#">Paella</a> at <a href="#">La Boqueria Market</a>.</li>
        <li><strong>Afternoon:</strong> Relax at <a href="#">Barceloneta Beach</a>.</li>
        <li><strong>Evening:</strong> Walk <a href="#">La Rambla</a> and enjoy <a href="#">Sangria</a> at a rooftop bar.</li>
    </ul>
</div>
"""

# List of hardcoded itineraries for use in views (instead of a database)
user_itineraries = [
    ItineraryDetails(
        id=1,
        name="Backpacking Through Europe",
        user="JaneDoe",
        destination="Europe",
        duration=4,
        budget=3000.00,
        star_rating="⭐⭐⭐☆☆",
        review_count=10,
        visibility="public",
        details=itinerary_details_html
    ),
    ItineraryDetails(
        id=2,
        name="Asian Cultural Tour",
        user="JohnSmith",
        destination="Japan, South Korea, Vietnam",
        duration=10,
        budget=2500.00,
        star_rating="☆☆☆☆☆",
        review_count=0,
        visibility="private",
        details="""
    <h2>Asian Cultural Tour </h2>
    <h3><span class="stars">⭐⭐⭐⭐☆</span></h3>
    <div class="itinerary-box">
        <!-- Day 1 -->
        <h3>📅 Day 1: <a href="#">Kyoto, Japan</a></h3>
        <ul>
            <li><strong>Morning:</strong> Visit <a href="#">Fushimi Inari Shrine</a>.</li>
            <li><strong>Lunch:</strong> Sample ramen at <a href="#">Ichiran</a>.</li>
            <li><strong>Afternoon:</strong> Explore <a href="#">Gion District</a>.</li>
        </ul>
    </div>
    """
    ),
]

public_itineraries = [
    ItineraryDetails(
        id=1,
        name="Backpacking Through Europe",
        user="JaneDoe",
        destination="Europe",
        duration=4,
        budget=3000.00,
        star_rating="⭐⭐⭐☆☆",
        review_count=10,
        visibility="public",
        details=itinerary_details_html
    ),
    ItineraryDetails(
        id=2,
        name="Asian Cultural Tour",
        user="JohnSmith",
        destination="Japan, South Korea, Vietnam",
        duration=10,
        budget=2500.00,
        star_rating="⭐⭐⭐⭐☆",
        review_count=205,
        visibility="public",
        details="""
    <h2>Asian Cultural Tour </h2>
    <h3><span class="stars">⭐⭐⭐⭐☆</span></h3>
    <div class="itinerary-box">
        <!-- Day 1 -->
        <h3>📅 Day 1: <a href="#">Kyoto, Japan</a></h3>
        <ul>
            <li><strong>Morning:</strong> Visit <a href="#">Fushimi Inari Shrine</a>.</li>
            <li><strong>Lunch:</strong> Sample ramen at <a href="#">Ichiran</a>.</li>
            <li><strong>Afternoon:</strong> Explore <a href="#">Gion District</a>.</li>
        </ul>
    </div>
    """
    ),
]