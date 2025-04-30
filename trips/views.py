from decimal import Decimal, InvalidOperation

from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, redirect, Http404, get_object_or_404
from django.urls import reverse
from .models import Itinerary, User, Comment
from actions.models import Action
from django.db.models import F, Q
from django.utils.timezone import now, timedelta
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt

from django.contrib import messages

# Renders the saved itineraries list for logged-in user
def saved_itineraries_list(request):
    if not request.session.get('username'):
        return redirect('user:login')

    sort = request.GET.get("sort", "date")
    username = request.session.get('username')
    if sort == "budget":
        # Order by budget ascending (0 or empty budgets will be on top)
        user_itineraries = Itinerary.objects.filter(user__username=username).order_by("budget")
    else:
        # Order by most recently updated first
        user_itineraries = Itinerary.objects.filter(user__username=username).order_by("-updated_at")

    return render(request, 'trips/itineraries/saved_itinerary_list.html', {
        'itineraries': user_itineraries,
        'current_sort': sort,
    })

# Renders the detail view of a specific itinerary using the hardcoded list
def user_itinerary_details(request, itinerary_id):
    username = request.session.get('username')
    user_itineraries = Itinerary.objects.filter(user__username=username)
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
    comments = itinerary.comments.filter(active=True).order_by('-created')
    return render(request, 'trips/itineraries/view_explore_itinerary_details.html', {
        'itinerary': itinerary,
        'comments': comments
    })

# Public explore page showing all itineraries
def explore_itineraries_list(request):
    username = request.session.get('username')
    if request.session.get('username'):
        public_itineraries = Itinerary.objects.filter(visibility='public').exclude(user__username=username)
    else:
        public_itineraries = Itinerary.objects.filter(visibility='public')

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
    if request.session.get("username", False):
        user = User.objects.get(username=request.session.get('username'))

        # 1) ContentType for Itinerary
        ct_itin = ContentType.objects.get_for_model(Itinerary)

        # 2) All the IDs of my itineraries
        my_itin_ids = Itinerary.objects.filter(user=user).values_list('id', flat=True)

        # 3) Filter Actions:
        actions = Action.objects.filter(
            Q(user=user)  # I performed it
            |  # OR
            (Q(target_ct=ct_itin) & Q(target_id__in=my_itin_ids))  # It affected one of my itineraries
        ).order_by('-created')[:100]

        return render(
            request,
            "trips/dashboard.html",
            {"actions": actions}
        )
    else:
        return render(
            request,
            "trips/home.html"
        )

# View to create a new itinerary
def create_itinerary(request):
    if not request.session.get("username", False):
        return redirect("user:login")

    username = request.session.get('username')
    user_itineraries = Itinerary.objects.filter(user__username=username)
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

        user = User.objects.get(username=request.session.get('username'))

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
            "author": request.session.get("username", "Anonymous"),
            "user": user,
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
            author=hardcoded_itinerary["author"],
            user=hardcoded_itinerary["user"],
            email=hardcoded_itinerary["email"],
        )
        itinerary.save()

        action = Action(
            user=user,
            verb="created an itinerary",
            target=itinerary
        )
        action.save()

        messages.add_message(request, messages.SUCCESS, "Itinerary created successfully!")

        user_itineraries = Itinerary.objects.filter(user__username=username).order_by(
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
            "message": f"The {itinerary.name} itinerary was saved successfully.",
            "redirect_url": redirect_url
        })
    else:
        messages.success(request, f"The {itinerary.name} itinerary was saved successfully.")
        return redirect(redirect_url)

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
                messages.add_message(request, messages.WARNING,
                                     f"The following itinerary was deleted successfully: {itinerary.name}")

                referer = request.META.get('HTTP_REFERER', '')

                user = User.objects.get(username=request.session.get('username'))
                action = Action(
                    user=user,
                    verb="deleted an itinerary",
                    target=itinerary
                )
                action.save()

                if 'explore' in referer:
                    return redirect('trips:user_shared_itinerary_details')
                elif 'itineraries' in referer:
                    return redirect('trips:saved_itineraries_list')
                else:
                    return redirect('home')
        except Itinerary.DoesNotExist:
            return JsonResponse({"success": False, "message": "Itinerary not found."}, status=404)
    return JsonResponse({"success": False, "message": "Invalid request method."}, status=400)

# Edit itinerary view
def edit_itinerary(request, itinerary_id):
    if not request.session.get('username'):
        return redirect('user:login')

    itinerary = get_object_or_404(Itinerary, id=itinerary_id)

    # Handle form submission
    if request.method == "POST":
        print(request.POST.get('name', itinerary.name))

        changed_name = itinerary.name.lower().strip() == request.POST.get('name', itinerary.name).lower().strip()
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
        changed_details = itinerary.details.lower().strip() == request.POST.get('details', itinerary.details).lower().strip()
        itinerary.details = request.POST.get('details', itinerary.details)

        user = User.objects.get(username=request.session.get('username'))
        itinerary.save()

        if changed_name:
            action = Action(
                user=user,
                verb="edited the name of an itinerary",
                target=itinerary
            )
            action.save()
        if changed_details:
            action = Action(
                user=user,
                verb="edited the details of an itinerary",
                target=itinerary
            )
            action.save()

        messages.add_message(request, messages.INFO, f"The {itinerary.name} itinerary was edited successfully.")
        return redirect('trips:user_itinerary_details', itinerary_id=itinerary.id)

    # Render the edit form
    return render(request, 'trips/itineraries/edit_itinerary.html', {'itinerary': itinerary})

def add_comment(request, itinerary_id):
    itinerary = get_object_or_404(Itinerary, id=itinerary_id)
    if request.method == "POST":
        comment_text = request.POST.get('comment', '').strip()
        if not comment_text:
            messages.error(request, "Comment cannot be empty.")
            return redirect('trips:user_shared_itinerary_details', itinerary_id=itinerary_id)
        # Get the current user based on the session
        user = get_object_or_404(User, username=request.session.get('username'))
        # Create and save the new comment associated with the itinerary
        new_comment = Comment(
            itinerary=itinerary,
            user=user,
            email=user.email,
            body=comment_text
        )
        new_comment.save()

        action = Action(
            user=user,
            verb="commented on an itinerary",
            target=itinerary
        )
        action.save()

        messages.success(request, "Comment added successfully!")
        return redirect('trips:user_shared_itinerary_details', itinerary_id=itinerary_id)
    return redirect('trips:user_shared_itinerary_details', itinerary_id=itinerary_id)

@csrf_exempt
def delete_comment(request, comment_id):
    if request.method == "POST":
        try:
            comment = Comment.objects.get(id=comment_id)
            comment.delete()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                print("Ajax")
                return JsonResponse({"success": True, "message": f"The comment created on {comment.created} was deleted successfully."})
            else:
                print("Server")
                messages.add_message(request, messages.WARNING,
                                     f"The comment created on {comment.created} was deleted successfully.")
                return redirect('trips:user_shared_itinerary_details', itinerary_id=comment.itinerary.id)
        except Itinerary.DoesNotExist:
            return JsonResponse({"success": False, "message": "Itinerary not found."}, status=404)
    return JsonResponse({"success": False, "message": "Invalid request method."}, status=400)