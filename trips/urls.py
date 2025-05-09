from django.urls import path
from . import views
app_name = 'trips'
urlpatterns = [
    path('', views.home, name='home'),
    path('itineraries/', views.saved_itineraries_list, name='saved_itineraries_list'),
    path('itineraries/<int:itinerary_id>/', views.user_itinerary_details, name='user_itinerary_details'),
    path('itineraries/<int:itinerary_id>/edit/', views.edit_itinerary, name='edit_itinerary'),
    path('itineraries/<int:itinerary_id>/delete/', views.delete_itinerary, name='delete_itinerary'),
    path('itineraries/<int:itinerary_id>/add_comment/', views.add_comment, name='add_comment'),

    path('explore/<int:itinerary_id>/', views.user_shared_itinerary_details,
         name='user_shared_itinerary_details'),
    path('explore/', views.explore_itineraries_list, name='explore_itineraries_list'),

    path('create/', views.create_itinerary, name='create_itinerary'),
    path('save_itinerary/<int:itinerary_id>/', views.save_itinerary, name='save_itinerary'),
    path('itineraries/<int:itinerary_id>/delete/', views.delete_itinerary, name='delete_itinerary'),
    path('itineraries/<int:itinerary_id>/add_comment/', views.add_comment, name='add_comment'),
    path('itineraries/<int:comment_id>/delete_comment/', views.delete_comment, name='delete_comment')
]