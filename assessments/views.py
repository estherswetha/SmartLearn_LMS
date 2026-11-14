
import csv
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse

from .models import Assessment, Question, AssessmentTag
from .forms import AssessmentForm, QuestionForm
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone

from .models import AssessmentAssignment
from .assignment_forms import StudentAssignmentForm

# =====================================================
# 1. ASSESSMENT DASHBOARD
# =====================================================

@login_required
def assessment_dashboard(request):

    all_assessments = Assessment.objects.filter(
        created_by=request.user,
        archived=False
    ).order_by("-created_at")

    search_query = request.GET.get("search", "").strip()
    selected_status = request.GET.get("status", "")

    assessments = all_assessments

    if search_query:
        assessments = assessments.filter(
            Q(title__icontains=search_query)
        )

    if selected_status in ["draft", "published", "closed"]:
        assessments = assessments.filter(
            status=selected_status
        )

    context = {
        "assessments": assessments,
        "search_query": search_query,
        "selected_status": selected_status,
        "total_assessments": all_assessments.count(),
        "draft_count": all_assessments.filter(
            status="draft"
        ).count(),
        "published_count": all_assessments.filter(
            status="published"
        ).count(),
        "closed_count": all_assessments.filter(
            status="closed"
        ).count(),
    }

    return render(
        request,
        "assessments/dashboard.html",
        context
    )


# =====================================================
# 2. CREATE ASSESSMENT
# =====================================================

@login_required
def create_assessment(request):

    if request.method == "POST":

        form = AssessmentForm(request.POST)

        if form.is_valid():

            assessment = form.save(commit=False)
            assessment.created_by = request.user
            assessment.save()

            messages.success(
                request,
                "Assessment created successfully!"
            )

            return redirect(
                "assessments:dashboard"
            )

    else:
        form = AssessmentForm()

    return render(
        request,
        "assessments/create_assessment.html",
        {
            "form": form
        }
    )


# =====================================================
# 3. ASSESSMENT DETAIL
# =====================================================

@login_required
def assessment_detail(request, pk):

    assessment = get_object_or_404(
        Assessment,
        pk=pk,
        created_by=request.user
    )

    questions = assessment.questions.all().order_by("id")

    total_questions = questions.count()

    total_marks = sum(
        question.marks
        for question in questions
    )

    context = {
        "assessment": assessment,
        "questions": questions,
        "total_questions": total_questions,
        "total_marks": total_marks,
    }

    return render(
        request,
        "assessments/assessment_detail.html",
        context
    )


# =====================================================
# 4. ADD QUESTION
# =====================================================

@login_required
def add_question(request, pk):

    assessment = get_object_or_404(
        Assessment,
        pk=pk,
        created_by=request.user
    )

    if assessment.status != "draft":

        messages.error(
            request,
            "You cannot add questions to a published or closed assessment."
        )

        return redirect(
            "assessments:detail",
            pk=assessment.pk
        )

    if request.method == "POST":

        form = QuestionForm(request.POST)

        if form.is_valid():

            question = form.save(commit=False)
            question.assessment = assessment
            question.save()

            messages.success(
                request,
                "Question added successfully!"
            )

            return redirect(
                "assessments:detail",
                pk=assessment.pk
            )

        messages.error(
            request,
            "Please correct the errors below."
        )

    else:
        form = QuestionForm()

    return render(
        request,
        "assessments/add_question.html",
        {
            "form": form,
            "assessment": assessment
        }
    )


# =====================================================
# 5. ARCHIVE ASSESSMENT
# =====================================================

@login_required
def archive_assessment(request, pk):

    if request.method == "POST":

        assessment = get_object_or_404(
            Assessment,
            pk=pk,
            created_by=request.user
        )

        assessment.archived = True

        assessment.save(
            update_fields=["archived"]
        )

        messages.success(
            request,
            "Assessment archived successfully!"
        )

    return redirect(
        "assessments:dashboard"
    )


# =====================================================
# 6. VIEW ARCHIVED ASSESSMENTS
# =====================================================

@login_required
def archived_assessments(request):

    assessments = Assessment.objects.filter(
        created_by=request.user,
        archived=True
    ).order_by("-created_at")

    return render(
        request,
        "assessments/management_page.html",
        {
            "page_title": "Archived Assessments",
            "assessments": assessments,
            "page_type": "archive",
        }
    )


# =====================================================
# 7. RESTORE ASSESSMENT
# =====================================================

@login_required
def restore_assessment(request, pk):

    if request.method == "POST":

        assessment = get_object_or_404(
            Assessment,
            pk=pk,
            created_by=request.user
        )

        assessment.archived = False

        assessment.save(
            update_fields=["archived"]
        )

        messages.success(
            request,
            "Assessment restored successfully!"
        )

    return redirect(
        "assessments:archived"
    )


# =====================================================
# 8. QUESTION BANK
# =====================================================

@login_required
def question_bank(request):

    questions = Question.objects.filter(
        assessment__created_by=request.user,
        assessment__archived=False
    ).select_related(
        "assessment"
    ).order_by("-id")

    search = request.GET.get(
        "search", ""
    ).strip()

    if search:

        questions = questions.filter(
            Q(question_text__icontains=search)
            | Q(assessment__title__icontains=search)
        )

    return render(
        request,
        "assessments/management_page.html",
        {
            "page_title": "Question Bank",
            "questions": questions,
            "search_query": search,
            "page_type": "questions",
        }
    )


# =====================================================
# 9. ASSESSMENT TAGS
# =====================================================

@login_required
def assessment_tags(request):

    if request.method == "POST":

        name = request.POST.get(
            "name", ""
        ).strip()

        if name:

            tag, created = AssessmentTag.objects.get_or_create(
                name=name,
                created_by=request.user
            )

            if created:

                messages.success(
                    request,
                    "Tag created successfully!"
                )

            else:

                messages.info(
                    request,
                    "This tag already exists."
                )

        return redirect(
            "assessments:tags"
        )

    tags = AssessmentTag.objects.filter(
        created_by=request.user
    ).order_by("name")

    return render(
        request,
        "assessments/management_page.html",
        {
            "page_title": "Assessment Tags",
            "tags": tags,
            "page_type": "tags",
        }
    )


# =====================================================
# 10. DELETE TAG
# =====================================================

@login_required
def delete_tag(request, pk):

    if request.method == "POST":

        tag = get_object_or_404(
            AssessmentTag,
            pk=pk,
            created_by=request.user
        )

        tag.delete()

        messages.success(
            request,
            "Tag deleted successfully."
        )

    return redirect(
        "assessments:tags"
    )


# =====================================================
# 11. ASSESSMENT SUMMARY
# =====================================================

@login_required
def assessment_summary(request):

    assessments = Assessment.objects.filter(
        created_by=request.user,
        archived=False
    )

    question_count = Question.objects.filter(
        assessment__created_by=request.user,
        assessment__archived=False
    ).count()

    context = {
        "page_title": "Assessment Summary",
        "page_type": "summary",
        "total": assessments.count(),
        "drafts": assessments.filter(
            status="draft"
        ).count(),
        "published": assessments.filter(
            status="published"
        ).count(),
        "closed": assessments.filter(
            status="closed"
        ).count(),
        "question_count": question_count,
    }

    return render(
        request,
        "assessments/management_page.html",
        context
    )


# =====================================================
# 12. EXPORT QUESTION BANK TO CSV
# =====================================================

@login_required
def export_question_bank(request):

    questions = Question.objects.filter(
        assessment__created_by=request.user
    ).select_related(
        "assessment"
    ).order_by(
        "assessment__title",
        "id"
    )

    response = HttpResponse(
        content_type="text/csv"
    )

    response["Content-Disposition"] = (
        'attachment; filename="smartlearn_question_bank.csv"'
    )

    writer = csv.writer(response)

    writer.writerow([
        "Assessment",
        "Question",
        "Question Type",
        "Options",
        "Correct Answer",
        "Marks",
    ])

    for question in questions:

        writer.writerow([
            question.assessment.title,
            question.question_text,
            question.get_question_type_display(),
            json.dumps(
                question.options or [],
                ensure_ascii=False
            ),
            question.correct_answer,
            question.marks,
        ])

    return response

# =====================================================
# 13. ASSIGN ASSESSMENT TO STUDENTS
# =====================================================

import uuid


@login_required
def assign_students(request, pk):

    assessment = get_object_or_404(
        Assessment,
        pk=pk,
        created_by=request.user,
        archived=False
    )

    if assessment.status != "draft":
        messages.error(
            request,
            "Only draft assessments can be assigned."
        )
        return redirect(
            "assessments:detail",
            pk=assessment.pk
        )

    if not assessment.questions.exists():
        messages.error(
            request,
            "Please add questions before assigning students."
        )
        return redirect(
            "assessments:detail",
            pk=assessment.pk
        )

    if request.method == "POST":

        form = StudentAssignmentForm(request.POST)

        if form.is_valid():

            students = form.cleaned_data["students"]

            created_count = 0
            existing_count = 0
            email_count = 0
            email_errors = []

            for student in students:

                assignment, created = (
                    AssessmentAssignment.objects.get_or_create(
                        assessment=assessment,
                        student=student
                    )
                )

                if created:
                    created_count += 1
                else:
                    existing_count += 1

                # Generate a token if an older assignment
                # does not yet have one.
                if not assignment.access_token:
                    assignment.access_token = uuid.uuid4()
                    assignment.save(
                        update_fields=["access_token"]
                    )

                if not student.email:
                    email_errors.append(
                        f"{student.username}: no email address"
                    )
                    continue

                relative_url = reverse(
                    "assessments:student_start",
                    kwargs={
                        "token": assignment.access_token
                    }
                )

                assessment_url = request.build_absolute_uri(
                    relative_url
                )

                subject = (
                    f"SmartLearn Assessment: {assessment.title}"
                )

                message = (
                    f"Hello {student.get_full_name() or student.username},\n\n"
                    f"You have been assigned an assessment.\n\n"
                    f"Assessment: {assessment.title}\n"
                    f"Start date: {timezone.localtime(assessment.start_date)}\n"
                    f"End date: {timezone.localtime(assessment.end_date)}\n"
                    f"Duration: {assessment.duration} minutes\n\n"
                    f"Your assessment link:\n{assessment_url}\n\n"
                    "Please sign in to your SmartLearn account "
                    "to access your assessment.\n"
                )

                try:

                    send_mail(
                        subject,
                        message,
                        getattr(
                            settings,
                            "DEFAULT_FROM_EMAIL",
                            None
                        ),
                        [student.email],
                        fail_silently=False
                    )

                    assignment.email_sent = True
                    assignment.save(
                        update_fields=["email_sent"]
                    )

                    email_count += 1

                except Exception as error:

                    email_errors.append(
                        f"{student.username}: {str(error)}"
                    )

            messages.success(
                request,
                (
                    f"{created_count} new assignments created. "
                    f"{existing_count} assignments already existed. "
                    f"{email_count} invitation emails sent."
                )
            )

            if email_errors:
                messages.warning(
                    request,
                    "Some invitations could not be sent: "
                    + "; ".join(email_errors)
                )

            return redirect(
                "assessments:detail",
                pk=assessment.pk
            )

    else:
        form = StudentAssignmentForm()

    return render(
        request,
        "assessments/assign_students.html",
        {
            "assessment": assessment,
            "form": form
        }
    )
