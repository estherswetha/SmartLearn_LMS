
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Workshop, WorkshopRegistration, WorkshopHistory


def log_workshop(workshop, action, details=""):
    WorkshopHistory.objects.create(
        workshop=workshop,
        workshop_title=workshop.title,
        action=action,
        details=details,
    )


def workshop_list(request):
    workshops = Workshop.objects.all()

    return render(
        request,
        "workshops/workshop_list.html",
        {"workshops": workshops},
    )



def create_workshop(request):
    # Show the form when the user clicks Create Workshop
    if request.method == "GET":
        return render(
            request,
            "workshops/create_workshop.html",
        )

    # Read the submitted form
    title = request.POST.get("title", "").strip()
    instructor = request.POST.get("instructor", "").strip()
    topic = request.POST.get("topic", "General").strip()
    start_time_text = request.POST.get("start_time", "").strip()
    description = request.POST.get("description", "").strip()
    meeting_url = request.POST.get("meeting_url", "").strip()

    try:
        price = Decimal(request.POST.get("price", "0") or "0")
        duration = int(request.POST.get("duration_minutes", "60") or "60")
        capacity = int(request.POST.get("capacity", "30") or "30")

        if not title or not instructor or not start_time_text:
            raise ValueError("Title, instructor and date/time are required.")

        if price < 0 or duration < 1 or capacity < 1:
            raise ValueError("Enter a valid price, duration and capacity.")

        start_time = timezone.datetime.fromisoformat(start_time_text)

        if timezone.is_naive(start_time):
            start_time = timezone.make_aware(
                start_time,
                timezone.get_current_timezone(),
            )

        if meeting_url and not meeting_url.startswith(("https://", "http://")):
            raise ValueError("Enter a valid meeting URL.")

        workshop = Workshop.objects.create(
            title=title,
            instructor=instructor,
            topic=topic or "General",
            start_time=start_time,
            description=description,
            meeting_url=meeting_url,
            price=price,
            duration_minutes=duration,
            capacity=capacity,
        )

        log_workshop(workshop, "Created", "Workshop created by host.")
        messages.success(request, "Workshop created successfully!")

        return redirect("workshop_detail", pk=workshop.pk)

    except (ValueError, InvalidOperation, TypeError) as error:
        messages.error(request, str(error))
        return render(
            request,
            "workshops/create_workshop.html",
            {"form_data": request.POST},
        )


    return redirect("workshop_list")


def workshop_detail(request, pk):
    workshop = get_object_or_404(Workshop, pk=pk)
    email = request.session.get("workshop_email", "")
    registration = None

    if email:
        registration = WorkshopRegistration.objects.filter(
            workshop=workshop,
            student_email=email,
        ).first()

    return render(
        request,
        "workshops/workshop_detail.html",
        {
            "workshop": workshop,
            "registration": registration,
        },
    )


def register_workshop(request, pk):
    if request.method != "POST":
        return redirect("workshop_detail", pk=pk)

    workshop = get_object_or_404(Workshop, pk=pk)
    name = request.POST.get("student_name", "").strip()
    email = request.POST.get("student_email", "").strip().lower()

    if not name or not email:
        messages.error(request, "Enter your name and email to register.")
        return redirect("workshop_detail", pk=pk)

    if workshop.price != 0:
        messages.error(request, "This workshop requires a paid-registration system.")
        return redirect("workshop_detail", pk=pk)

    if workshop.status in ("completed", "cancelled"):
        messages.error(request, "Registration is closed for this workshop.")
        return redirect("workshop_detail", pk=pk)

    if workshop.start_time <= timezone.now():
        messages.error(request, "This workshop has already started.")
        return redirect("workshop_detail", pk=pk)

    if workshop.registered_count >= workshop.capacity:
        messages.error(request, "Sorry, this workshop is full.")
        return redirect("workshop_detail", pk=pk)

    registration, created = WorkshopRegistration.objects.get_or_create(
        workshop=workshop,
        student_email=email,
        defaults={"student_name": name},
    )

    if created:
        log_workshop(workshop, "Registered", f"Student registered: {email}")
        messages.success(request, "You have registered successfully!")
    else:
        messages.info(request, "This email is already registered.")

    request.session["workshop_email"] = email
    return redirect("workshop_detail", pk=pk)


@require_POST
def cancel_registration(request, pk):
    workshop = get_object_or_404(Workshop, pk=pk)
    email = request.session.get("workshop_email", "")

    if not email:
        messages.error(request, "Register first to manage your registration.")
        return redirect("workshop_detail", pk=pk)

    registration = WorkshopRegistration.objects.filter(
        workshop=workshop,
        student_email=email,
    ).first()

    if registration:
        registration.delete()
        log_workshop(workshop, "Registration cancelled", email)
        messages.success(request, "Registration cancelled.")
    else:
        messages.info(request, "No registration was found.")

    return redirect("workshop_detail", pk=pk)


def join_workshop(request, pk):
    workshop = get_object_or_404(Workshop, pk=pk)
    email = request.session.get("workshop_email", "")

    registration = WorkshopRegistration.objects.filter(
        workshop=workshop,
        student_email=email,
    ).first()

    if not registration:
        messages.error(request, "Register for this workshop before joining.")
        return redirect("workshop_detail", pk=pk)

    if workshop.status in ("completed", "cancelled"):
        messages.error(request, "This workshop is no longer live.")
        return redirect("workshop_detail", pk=pk)

    if workshop.start_time > timezone.now():
        messages.info(request, "The workshop has not started yet.")
        return redirect("workshop_detail", pk=pk)

    if not workshop.meeting_url:
        messages.error(request, "The host has not added a meeting link yet.")
        return redirect("workshop_detail", pk=pk)

    if workshop.status == "upcoming":
        workshop.status = "live"
        workshop.save(update_fields=["status", "updated_at"])
        log_workshop(workshop, "Live", "Workshop marked live.")

    return redirect(workshop.meeting_url)


@require_POST
def update_attendance(request, pk, registration_id):
    workshop = get_object_or_404(Workshop, pk=pk)
    registration = get_object_or_404(
        WorkshopRegistration,
        pk=registration_id,
        workshop=workshop,
    )

    registration.attended = request.POST.get("attended") == "yes"
    registration.save(update_fields=["attended"])

    log_workshop(
        workshop,
        "Attendance updated",
        f"{registration.student_email}: {registration.attended}",
    )

    messages.success(request, "Attendance updated.")
    return redirect("workshop_detail", pk=pk)


@require_POST
def complete_workshop(request, pk):
    workshop = get_object_or_404(Workshop, pk=pk)
    recording_url = request.POST.get("recording_url", "").strip()

    workshop.status = "completed"
    if recording_url:
        workshop.recording_url = recording_url

    workshop.save(update_fields=["status", "recording_url", "updated_at"])
    log_workshop(workshop, "Completed", "Workshop marked completed.")

    messages.success(request, "Workshop marked as completed.")
    return redirect("workshop_detail", pk=pk)


def workshop_history(request):
    history = WorkshopHistory.objects.all()

    return render(
        request,
        "workshops/workshop_history.html",
        {"history": history},
    )
