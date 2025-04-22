# trips/models.py
from decimal import Decimal

from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils.timezone import now

# Django model representing saved itineraries in the database
class Itinerary(models.Model):
    # Choices for visibility field
    VISIBILITY_CHOICES = (
        ('public', 'Public'),
        ('private', 'Private'),
    )

    REGION_CHOICES = (
        ('europe', 'Europe'),
        ('asia', 'Asia'),
        ('africa', 'Africa'),
        ('antarctica', 'Antarctica'),
        ('north-america', 'North America'),
        ('south-america', 'South America'),
        ('australia', 'Australia'),
        ('mid-east', 'Middle East'),
        ('pacific', 'Pacific')
    )

    # Name of the itinerary
    name = models.CharField(max_length=200, default="My Itinerary")

    user = models.CharField(max_length=150, default='Anonymous')
    email = models.CharField(max_length=150, default='Anonymous')

    # Destination name(s)
    destination = models.CharField(max_length=200, blank=True)

    # Budget for the trip
    budget = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    # Star rating (optional)
    star_rating = models.CharField(max_length=10, blank=True)

    # Number of reviews
    review_count = models.PositiveIntegerField(blank=True, default=0)

    # Visibility setting: 'public' or 'private'
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default="public")

    region = models.CharField(max_length=75, choices=REGION_CHOICES)

    start_date = models.DateField(help_text="Optional start date of the itinerary")
    end_date = models.DateField(help_text="Optional end date of the itinerary")

    created_at = models.DateTimeField(auto_now_add=True, help_text="The time this itinerary was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="The time this itinerary was last updated.")
    details = models.TextField(blank=True, help_text="Detailed description of the itinerary")
    save_model = models.BooleanField(default=False, help_text="Is this itinerary saved?")

    @property
    def duration(self):
        return (self.end_date - self.start_date).days

    # String representation for Django admin or debugging
    def __str__(self):
        return self.name