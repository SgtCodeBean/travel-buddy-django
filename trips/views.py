from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, Http404, get_object_or_404
from django.urls import reverse
from .models import Itinerary
from django.db.models import F
from django.utils.timezone import now, timedelta
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

# Renders the saved itineraries list for logged-in users
def saved_itineraries_list(request):
    if not request.session.get('username'):
        return redirect('trips:login')

    sort = request.GET.get("sort", "date")
    if sort == "budget":
        # Order by budget ascending (0 or empty budgets will be on top)
        user_itineraries = Itinerary.objects.filter(email=request.session.get('username')).order_by("budget")
    else:
        # Order by most recently updated first
        user_itineraries = Itinerary.objects.filter(email=request.session.get('username')).order_by("-updated_at")

    return render(request, 'trips/itineraries/saved_itinerary_list.html', {
        'itineraries': user_itineraries,
        'current_sort': sort,
    })

# Renders the detail view of a specific itinerary using the hardcoded list
def user_itinerary_details(request, itinerary_id):
    user_itineraries = Itinerary.objects.filter(email=request.session.get('username'))
    itinerary = next((it for it in user_itineraries if it.id == itinerary_id), None)
    if itinerary is None:
        raise Http404("Itinerary does not exist")
    return render(request, 'trips/itineraries/user_itinerary_details.html', {'itinerary': itinerary})

# View itinerary details in the "explore" section
def user_shared_itinerary_details(request, itinerary_id):
    public_itineraries = Itinerary.objects.filter(visibility='public')
    itinerary = next((it for it in public_itineraries if it.id == itinerary_id), None)
    if itinerary is None:
        raise Http404("Itinerary does not exist")
    return render(request, 'trips/itineraries/view_explore_itinerary_details.html', {'itinerary': itinerary})

# Public explore page showing all itineraries
def explore_itineraries_list(request):
    current_user_email = request.session.get('username')
    public_itineraries = Itinerary.objects.filter(visibility='public').exclude(email=current_user_email)
    if not request.session.get('username'):
        return redirect('trips:login')

    sort = request.GET.get("sort", "date")
    if sort == "budget":
        # Order by budget ascending (0 or empty budgets will be on top)
        public_itineraries = public_itineraries.order_by("budget")
    else:
        # Order by most recently updated first
        public_itineraries = public_itineraries.order_by("-updated_at")

    return render(request, 'trips/itineraries/explore_itineraries_list.html', {
        'itineraries': public_itineraries,
        'current_sort': sort,
    })

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

# View to create a new itinerary
def create_itinerary(request):
    if not request.session.get("username", False):
        return redirect("trips:login")

    user_itineraries = Itinerary.objects.filter(email=request.session.get('username'))
    if request.method == "POST":
        # Extract user inputs from the form
        region = request.POST.getlist("region[]", [])
        start_date = request.POST.get("start-date", now().date())
        end_date = request.POST.get("end-date", (now() + timedelta(days=7)).date())

        errors = []
        if not region:
            errors.append("Please select at least one region.")
        if end_date < start_date:
            errors.append("End date cannot be before start date.")

        if errors:
            return JsonResponse({"errors": errors}, status=400)

        raw_budget = request.POST.get("budget", "").strip()
        try:
            # if empty, default to 0.00
            budget = Decimal(raw_budget) if raw_budget else Decimal("0.00")
        except InvalidOperation:
            # someone entered “abc” or something invalid — fall back to zero
            budget = Decimal("0.00")
        travel_type = request.POST.get("travel-type", "solo")
        custom_preferences = request.POST.get("custom-preferences", "")

        # Simulate chatbot response
        chatbot_response = f"Great! Here's a suggested itinerary for your trip to {', '.join(region) or 'Anywhere'}."

        # Hardcoded itinerary details
        hardcoded_itinerary = {
            "name": "European Adventure",
            "destination": "Paris, Rome, Berlin",
            "details": "Explore the Eiffel Tower, Colosseum, and Brandenburg Gate.",
            "region": region[0] if region else "europe",
            "visibility": "private",
            "budget": budget,
            "start_date": start_date,
            "end_date": end_date,
            "user": request.session.get("username", "Anonymous").split("@")[0],
            "email": request.session.get("username", "Anonymous"),
        }

        # Save the itinerary to the database
        itinerary = Itinerary(
            name=hardcoded_itinerary["name"],
            destination=hardcoded_itinerary["destination"],
            details=hardcoded_itinerary["details"],
            region=hardcoded_itinerary["region"],
            visibility=hardcoded_itinerary["visibility"],
            budget=hardcoded_itinerary["budget"],
            start_date=hardcoded_itinerary["start_date"],
            end_date=hardcoded_itinerary["end_date"],
            user=hardcoded_itinerary["user"],
            email=hardcoded_itinerary["email"],
        )
        itinerary.save()
        messages.add_message(request, messages.SUCCESS, "Itinerary created successfully!")

        user_itineraries = Itinerary.objects.filter(email=request.session.get('username')).order_by(
            F('updated_at').desc())
        # Return a simulated chatbot response
        return JsonResponse({
            "success": True,
            "message": f"Great! Here's a suggested itinerary for your trip to {', '.join(region)}.\n{itinerary.details}",
            "itineraries": list(
                user_itineraries.values("id", "name", "destination", "start_date", "end_date", "budget", "updated_at"))
        })

    return render(request, 'trips/itineraries/create_itinerary.html', {'itineraries': user_itineraries})

def save_itinerary(request, itinerary_id):
    if request.method != "POST":
        return redirect('trips:saved_itineraries_list')

    itinerary = get_object_or_404(Itinerary, id=itinerary_id)
    itinerary.save_model = True
    itinerary.save()

    redirect_url = reverse('trips:user_itinerary_details', kwargs={'itinerary_id': itinerary_id})
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            "success": True,
            "message": "Itinerary saved successfully.",
            "redirect_url": redirect_url
        })
    else:
        messages.success(request, "Itinerary saved successfully!")
        return redirect(redirect_url)

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

# Delete itinerary view
@csrf_exempt
def delete_itinerary(request, itinerary_id):
    if request.method == "POST":
        try:
            itinerary = Itinerary.objects.get(id=itinerary_id)
            itinerary.delete()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": True, "message": f"The {itinerary.name} itinerary was deleted successfully."})
            else:
                messages.add_message(request, messages.WARNING, f"The following itinerary was deleted successfully: {itinerary.name}")
                return JsonResponse({"success": True, "message": f"The {itinerary.name} itinerary was deleted successfully."})
        except Itinerary.DoesNotExist:
            return JsonResponse({"success": False, "message": "Itinerary not found."}, status=404)
    return JsonResponse({"success": False, "message": "Invalid request method."}, status=400)

# Simulated add comment functionality (does not store the comment)
def add_comment(request, itinerary_id):
    if request.method == "POST":
        comment = request.POST.get('comment')
        # Just simulate success message for now
        messages.success(request, "Comment added successfully! (Simulated)")
        return redirect('trips:user_shared_itinerary_details', itinerary_id=itinerary_id)
    else:
        return redirect('trips:user_shared_itinerary_details', itinerary_id=itinerary_id)

# Edit itinerary view
def edit_itinerary(request, itinerary_id):
    if not request.session.get('username'):
        return redirect('trips:login')

    itinerary = get_object_or_404(Itinerary, id=itinerary_id)

    # Handle form submission
    if request.method == "POST":
        print(request.POST.get('name', itinerary.name))
        itinerary.name = request.POST.get('name', itinerary.name)
        itinerary.region = request.POST.get('region', itinerary.region)
        itinerary.visibility = request.POST.get('visibility', itinerary.visibility)

        start_date_str = request.POST.get('start_date')
        if start_date_str:
            itinerary.start_date = parse_date(start_date_str) or itinerary.start_date

        end_date_str = request.POST.get('end_date')
        if end_date_str:
            itinerary.end_date = parse_date(end_date_str) or itinerary.end_date

        try:
            itinerary.budget = float(request.POST.get('budget'))
        except (TypeError, ValueError):
            pass
        itinerary.details = request.POST.get('details', itinerary.details)

        itinerary.save()
        messages.add_message(request, messages.INFO, "The itinerary was edited successfully.")
        return redirect('trips:user_itinerary_details', itinerary_id=itinerary.id)

    # Render the edit form
    return render(request, 'trips/itineraries/edit_itinerary.html', {'itinerary': itinerary})