from django.shortcuts import render, redirect, Http404, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.urls import reverse
from .models import Itinerary, itineraries

# Renders the saved itineraries list for logged-in users
def saved_itineraries_list(request):
    if not request.session.get('username'):
        return redirect('trips:login')
    return render(request, 'trips/itineraries/saved_itinerary_list.html')

# Renders the detail view of a specific itinerary using the hardcoded list
def user_itinerary_details(request, itinerary_id):
    itinerary = next((it for it in itineraries if it.id == itinerary_id), None)
    if itinerary is None:
        raise Http404("Itinerary does not exist")
    return render(request, 'trips/itineraries/user_itinerary_details.html', {'itinerary': itinerary})

# Landing page view
def home(request):
    return render(request, 'trips/home.html')

# Simulated login view that uses hardcoded users
def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # Hard-coded user credentials
        users = {
            'regular_user@gmail.com': 'password123',
            'admin_user@gmail.com': 'adminpassword'
        }

        # Validate credentials
        if email in users and users[email] == password:
            request.session['username'] = email
            request.session['is_admin'] = (email == 'admin_user@gmail.com')
            next_url = request.session.get('next', reverse('trips:home'))
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid credentials')

    # Store next URL for redirection after login
    request.session['next'] = request.GET.get('next', reverse('trips:home'))
    return render(request, 'trips/login.html')

# View itinerary details in the "explore" section
def user_shared_itinerary_details(request, itinerary_id):
    return render(request, 'trips/itineraries/view_explore_itinerary.html', {'itinerary_id': itinerary_id})

# Public explore page showing all itineraries (not filtered)
def explore_itineraries_list(request):
    return render(request, 'trips/itineraries/explore_itineraries_list.html')

# Admin-only explore page showing itineraries from the database
def explore_itineraries_list_admin(request):
    if not request.session.get('is_admin'):
        return HttpResponseForbidden('You do not have permission to access this page.')
    itineraries = Itinerary.objects.all()
    return render(request, 'trips/itineraries/explore_itineraries_list_admin.html', {'itineraries': itineraries})

# Placeholder page for creating a new itinerary
def create_itinerary(request):
    return render(request, 'trips/itineraries/create_itinerary.html')

# Logout view that clears session
def logout(request):
    request.session.flush()
    return redirect('trips:home')

# Displays user profile page
def profile(request):
    return render(request, 'trips/profile.html')

# Page to create a new account (not functional in P4)
def create_account(request):
    return render(request, 'trips/create_account.html')

# Simulated deletion of an itinerary (does not actually delete)
def delete_itinerary(request, itinerary_id):
    if request.method == "POST":
        messages.success(request, f"Itinerary {itinerary_id} deleted.")
    return redirect('trips:explore_itineraries_list_admin')

# Simulated add comment functionality (does not store the comment)
def add_comment(request, itinerary_id):
    if request.method == "POST":
        comment = request.POST.get('comment')
        # Just simulate success message for now
        messages.success(request, "Comment added successfully! (Simulated)")
        return redirect('trips:user_shared_itinerary_details', itinerary_id=itinerary_id)
    else:
        return redirect('trips:user_shared_itinerary_details', itinerary_id=itinerary_id)


# Hardcoded mock itineraries used for editing functionality (not from DB)
mock_itineraries = {
    1: Itinerary(name="Trip to Japan", destination="Tokyo, Kyoto, Osaka", duration=14, budget=2500, star_rating="⭐⭐⭐⭐☆", review_count=24, visibility="public"),
    2: Itinerary(name="European Adventure", destination="Paris, Rome, Berlin", duration=21, budget=3500, star_rating="⭐⭐⭐☆☆", review_count=24, visibility="public"),
    3: Itinerary(name="Backpacking Southeast Asia", destination="Thailand, Vietnam, Indonesia", duration=30, budget=1800, star_rating="⭐⭐⭐⭐⭐", review_count=24, visibility="private"),
}

# Simulated edit view for changing the itinerary title
def edit_itinerary(request, itinerary_id):
    if not request.session.get('username'):
        return redirect('trips:login')

    itinerary = mock_itineraries.get(itinerary_id)
    if not itinerary:
        return render(request, '404.html', status=404)

    if request.method == "POST":
        new_title = request.POST.get("new_title")
        itinerary.name = new_title  # Simulate update
        return redirect('trips:saved_itineraries_list')

    return render(request, 'trips/itineraries/edit_itinerary.html', {'itinerary': itinerary})