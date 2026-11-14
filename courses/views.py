
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import Course, CourseHistory


def record_history(course, action, details=""):
    CourseHistory.objects.create(
        course=course,
        course_title=course.title,
        action=action,
        details=details,
    )


def my_courses(request):
    courses = Course.objects.order_by("-created_at")

    return render(request, "course_catalog.html", {
        "courses": courses,
        "course_count": courses.count(),
        "published_count": courses.filter(status="published").count(),
        "draft_count": courses.filter(status="draft").count(),
    })


def create_course(request):
    if request.method != "POST":
        return redirect("my_courses")

    title = request.POST.get("title", "").strip()
    description = request.POST.get("description", "").strip()
    category = request.POST.get("category", "other")
    status = request.POST.get("status", "draft")
    cover_emoji = request.POST.get("cover_emoji", "📚").strip()[:10]

    try:
        price = Decimal(request.POST.get("price", "0"))
        if not price.is_finite() or price < 0:
            raise InvalidOperation
    except (InvalidOperation, ValueError):
        messages.error(request, "Enter a valid, non-negative price.")
        return redirect("my_courses")

    valid_categories = {choice[0] for choice in Course.CATEGORY_CHOICES}
    valid_statuses = {choice[0] for choice in Course.STATUS_CHOICES}

    if not title:
        messages.error(request, "Please enter a course name.")
        return redirect("my_courses")

    if category not in valid_categories:
        category = "other"

    if status not in valid_statuses:
        status = "draft"

    course = Course.objects.create(
        title=title,
        description=description,
        category=category,
        price=price,
        status=status,
        cover_emoji=cover_emoji or "📚",
    )

    record_history(
        course,
        "created",
        f"Course created with status: {course.get_status_display()}.",
    )

    if status == "published":
        record_history(course, "published", "Course was published when created.")

    messages.success(request, f'"{title}" was created successfully!')
    return redirect("my_courses")


def edit_course(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if request.method == "POST":
        old_status = course.status
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        category = request.POST.get("category", "other")
        status = request.POST.get("status", "draft")
        cover_emoji = request.POST.get("cover_emoji", "📚").strip()[:10]

        try:
            price = Decimal(request.POST.get("price", "0"))
            if not price.is_finite() or price < 0:
                raise InvalidOperation
        except (InvalidOperation, ValueError):
            messages.error(request, "Enter a valid, non-negative price.")
            return redirect("edit_course", pk=course.pk)

        if not title:
            messages.error(request, "Course name is required.")
            return redirect("edit_course", pk=course.pk)

        valid_categories = {choice[0] for choice in Course.CATEGORY_CHOICES}
        valid_statuses = {choice[0] for choice in Course.STATUS_CHOICES}

        course.title = title
        course.description = description
        course.category = category if category in valid_categories else "other"
        course.status = status if status in valid_statuses else "draft"
        course.price = price
        course.cover_emoji = cover_emoji or "📚"
        course.save()

        record_history(course, "updated", "Course details were updated.")

        if old_status != course.status:
            if course.status == "published":
                record_history(course, "published", "Course status changed to Published.")
            else:
                record_history(course, "unpublished", "Course status changed to Draft.")

        messages.success(request, "Course updated successfully!")
        return redirect("my_courses")

    return render(request, "course_edit.html", {"course": course})


@require_POST
def delete_course(request, pk):
    course = get_object_or_404(Course, pk=pk)

    # Save history before deleting the course.
    record_history(
        course,
        "deleted",
        "Course was deleted from the course catalogue.",
    )

    title = course.title
    course.delete()

    messages.success(request, f'"{title}" was deleted.')
    return redirect("my_courses")


def launch_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    return render(request, "course_launch.html", {"course": course})


def course_history(request):
    history = CourseHistory.objects.all()

    return render(request, "course_history.html", {
        "history": history,
        "history_count": history.count(),
    })


def python_course(request):
    return render(request, "python_course.html")
