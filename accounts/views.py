from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from videos.models import LessonVideo

from urllib.parse import quote
from urllib.request import urlopen, Request

import json
import os
import time

from google import genai
from google.genai import types
from functools import wraps

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .forms import StudentRegistrationForm
from django.shortcuts import render
from .models import ScormCourse
from .scorm_forms import ScormCourseForm
# =========================================================
# GEMINI CONFIGURATION
# =========================================================

def get_gemini_client():
    """Create the Gemini client using the current GEMINI_API_KEY environment variable."""
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Set it in PowerShell before starting Django."
        )

    return genai.Client(api_key=api_key)


# =========================================================
# LOGIN
# =========================================================

def login_page(request):
    return render(request, "login.html")


# =========================================================
# DASHBOARD
# =========================================================

def dashboard(request):
    return render(request, "dashboard.html")

def my_courses(request):
    return render(request, "course_catalog.html")

# =========================================================
# LESSON 1
# =========================================================

def lesson1(request):
    lesson_video = LessonVideo.objects.filter(
        lesson_name="Lesson 1 - What is Python?"
    ).first()

    return render(
        request,
        "lesson1.html",
        {"lesson_video": lesson_video}
    )


# =========================================================
# ALL MODULES
# =========================================================

def all_modules(request):
    return render(request, "all_modules.html")


# =========================================================
# MODULE PAGE
# =========================================================

def module_page(request, module):

    if module == "learning":
        return render(request, "learning.html")

    if module == "languages":
        return render(request, "languages.html")

    if module == "videos":
        return render(request, "video_ai.html")

    if module == "summary":
        return render(request, "summary_ai.html")

    # NOTES AI
    if module == "notes":
        return render(request, "notes_ai.html")

    # ADAPTIVE AI
    if module == "adaptive":
        return render(request, "adaptive_ai.html")

    # QUIZ AI
    if module == "quizzes":
        return render(request, "quiz_ai.html")

    # TUTOR AI
    if module == "tutor":
        return render(request, "tutor_ai.html")

    # ANALYTICS AI
    if module == "analytics":
        return render(request, "analytics_ai.html")

    # VOICE AI
    if module == "voice":
        return render(request, "voice_ai.html")

    # GAMIFICATION
    if module == "gamification":
        return render(request, "gamification.html")

    # LEARNTWIN
    if module == "learntwin":
        return render(request, "learntwin.html")

    # =====================================================
    # COMMUNITY
    # =====================================================

    if module == "community":
        return render(request, "community.html")

    # OFFLINE MODULE
    if module == "offline":
        return render(request, "offline.html")

        # CAREER AI
    if module == "career":
        return render(request, "career_ai.html")

    # WORKSHOPS
    if module == "workshops":
        return redirect("/workshops/")

    # PORTFOLIO
    if module == "portfolio":
        return render(request, "portfolio.html")
    
    return render(
        request,
        "module.html",
        {"module": module}
    )


# =========================================================
# QUIZ AI PAGE
# =========================================================

def quiz_ai(request):
    return render(request, "quiz_ai.html")


# =========================================================
# QUIZ AI API
# =========================================================

@require_POST
def quiz_ai_api(request):

    subject = request.POST.get("subject", "").strip()
    topic = request.POST.get("topic", "").strip()
    difficulty = request.POST.get("difficulty", "Adaptive").strip()
    mode = request.POST.get("mode", "Adaptive").strip()

    print("=" * 60)
    print("QUIZ AI REQUEST")
    print("Subject:", subject)
    print("Topic:", topic)
    print("Difficulty:", difficulty)
    print("Mode:", mode)
    print("=" * 60)

    if not subject:
        return JsonResponse({
            "success": False,
            "error": "Please enter a subject."
        })

    if not topic:
        return JsonResponse({
            "success": False,
            "error": "Please enter a topic."
        })

    prompt = f"""
You are Quiz AI inside SmartLearn LMS.

Create an educational multiple-choice quiz for a student.

Subject: {subject}
Topic: {topic}
Difficulty: {difficulty}
Quiz Mode: {mode}

Create EXACTLY 5 questions.

Every question MUST contain:
- question
- exactly 4 options
- correct
- hint
- explanation

Each option MUST contain:
- value
- label

The option values MUST be exactly A, B, C, D.

Return ONLY valid JSON. Do not use Markdown or code fences.

Use exactly this structure:
{{
  "questions": [
    {{
      "question": "Question text",
      "options": [
        {{"value": "A", "label": "Option A"}},
        {{"value": "B", "label": "Option B"}},
        {{"value": "C", "label": "Option C"}},
        {{"value": "D", "label": "Option D"}}
      ],
      "correct": "A",
      "hint": "A useful hint that does not reveal the answer.",
      "explanation": "Explain why the correct answer is correct."
    }}
  ]
}}

Rules:
1. Return exactly 5 questions.
2. Return exactly 4 options for every question.
3. Correct must be A, B, C, or D.
4. Make all questions factually correct.
5. Make incorrect options plausible.
6. Avoid duplicate questions.
7. Keep explanations simple and educational.
8. Stay strictly within the selected subject and topic.
9. For Practice mode, focus on learning and revision.
10. For Detective mode, include debugging/code reasoning when appropriate.
11. For Adaptive mode, follow the selected difficulty.
"""

    try:
        client = get_gemini_client()

        models_to_try = [
            "gemini-3.6-flash",
            "gemini-3.5-flash",
            "gemini-3-flash",
            "gemini-3.5-flash-lite",
        ]

        response = None
        last_error = None

        for model_name in models_to_try:

            for attempt in range(2):

                try:
                    print("=" * 60)
                    print("QUIZ AI MODEL:", model_name)
                    print("ATTEMPT:", attempt + 1)
                    print("=" * 60)

                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                    )

                    if response and response.text:
                        break

                except Exception as model_error:

                    last_error = model_error

                    print(
                        "QUIZ AI MODEL ERROR:",
                        model_name,
                        model_error
                    )

                    error_text = str(model_error).upper()

                    if any(code in error_text for code in [
                        "429",
                        "503",
                        "UNAVAILABLE",
                        "RESOURCE_EXHAUSTED",
                        "TIMEOUT"
                    ]):
                        time.sleep(2 ** attempt)
                        continue

                    break

            if response and response.text:
                break

        if response is None or not response.text:

            error_text = str(last_error or "").upper()

            print("LAST QUIZ AI ERROR:", last_error)

            if "API_KEY" in error_text or "UNAUTHENTICATED" in error_text:
                user_error = (
                    "Gemini API key is missing or invalid. "
                    "Check GEMINI_API_KEY and restart Django."
                )

            elif "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
                user_error = (
                    "Gemini free-tier limit was reached. "
                    "Please wait a little and try again."
                )

            elif "403" in error_text or "PERMISSION" in error_text:
                user_error = (
                    "Gemini API access was denied. "
                    "Check that your Gemini API key is valid."
                )

            elif "404" in error_text or "NOT_FOUND" in error_text:
                user_error = (
                    "The Gemini model is not available for this API key. "
                    "Check Gemini API access."
                )

            else:
                user_error = (
                    "Quiz AI could not connect to Gemini. "
                    "Check the VS Code terminal for the exact error."
                )

            return JsonResponse({
                "success": False,
                "error": user_error
            }, status=503)

        text = response.text.strip()

        if text.startswith("```json"):
            text = text[7:]

        elif text.startswith("```"):
            text = text[3:]

        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

        first_brace = text.find("{")
        last_brace = text.rfind("}")

        if first_brace != -1 and last_brace > first_brace:
            text = text[first_brace:last_brace + 1]

        try:
            data = json.loads(text)

        except json.JSONDecodeError as error:

            print("QUIZ JSON ERROR:", error)
            print("TEXT RECEIVED:", text)

            return JsonResponse({
                "success": False,
                "error": (
                    "Gemini returned an invalid quiz format. "
                    "Please try again."
                )
            }, status=502)

        questions = data.get("questions")

        if not isinstance(questions, list):

            return JsonResponse({
                "success": False,
                "error": (
                    "Quiz AI did not return a valid "
                    "questions list."
                )
            }, status=502)

        if len(questions) != 5:

            return JsonResponse({
                "success": False,
                "error": (
                    f"Quiz AI returned {len(questions)} "
                    "questions instead of exactly 5. "
                    "Please generate again."
                )
            }, status=502)

        expected_values = ["A", "B", "C", "D"]

        normalized_questions = set()

        for index, question in enumerate(questions):

            question_number = index + 1

            if not isinstance(question, dict):

                return JsonResponse({
                    "success": False,
                    "error": (
                        f"Question {question_number} "
                        "is not in the correct format."
                    )
                }, status=502)

            question_text = str(
                question.get("question", "")
            ).strip()

            if not question_text:

                return JsonResponse({
                    "success": False,
                    "error": (
                        f"Question {question_number} "
                        "is missing question text."
                    )
                }, status=502)

            normalized = " ".join(
                question_text.lower().split()
            )

            if normalized in normalized_questions:

                return JsonResponse({
                    "success": False,
                    "error": (
                        "Quiz AI generated duplicate questions. "
                        "Please generate again."
                    )
                }, status=502)

            normalized_questions.add(normalized)

            options = question.get("options")

            if not isinstance(options, list) or len(options) != 4:

                return JsonResponse({
                    "success": False,
                    "error": (
                        f"Question {question_number} "
                        "must have exactly 4 options."
                    )
                }, status=502)

            for option_index, option in enumerate(options):

                expected_value = expected_values[option_index]

                if not isinstance(option, dict):

                    return JsonResponse({
                        "success": False,
                        "error": (
                            f"Option {option_index + 1} "
                            f"in question {question_number} "
                            "is invalid."
                        )
                    }, status=502)

                if option.get("value") != expected_value:

                    return JsonResponse({
                        "success": False,
                        "error": (
                            f"Question {question_number} "
                            "must have options A, B, C and D."
                        )
                    }, status=502)

                if not str(
                    option.get("label", "")
                ).strip():

                    return JsonResponse({
                        "success": False,
                        "error": (
                            f"Option {expected_value} "
                            f"in question {question_number} "
                            "is empty."
                        )
                    }, status=502)

            correct = question.get("correct")

            if correct not in expected_values:

                return JsonResponse({
                    "success": False,
                    "error": (
                        f"Question {question_number} "
                        "has an invalid correct answer."
                    )
                }, status=502)

            question["question"] = question_text

            question["hint"] = str(
                question.get("hint")
                or "Think carefully about the main concept."
            ).strip()

            question["explanation"] = str(
                question.get("explanation")
                or (
                    "This is the correct answer based "
                    "on the selected topic."
                )
            ).strip()

        answer_key = {
            str(index + 1): question["correct"]
            for index, question in enumerate(questions)
        }

        print("=" * 60)
        print("QUIZ AI SUCCESS")
        print("Questions:", len(questions))
        print("Subject:", subject)
        print("Topic:", topic)
        print("=" * 60)

        return JsonResponse({
            "success": True,
            "questions": questions,
            "total_questions": 5,
            "subject": subject,
            "topic": topic,
            "difficulty": difficulty,
            "mode": mode,
            "answer_key": answer_key,
            "message": "Quiz generated successfully!"
        })

    except Exception as error:

        print("=" * 60)
        print("QUIZ AI REAL ERROR")
        print("ERROR TYPE:", type(error).__name__)
        print("ERROR:", str(error))
        print("=" * 60)

        error_text = str(error)
        upper_error = error_text.upper()

        if "GEMINI_API_KEY IS NOT SET" in upper_error:

            user_error = (
                "GEMINI_API_KEY is not set. "
                "Set it in PowerShell and restart Django."
            )

        elif (
            "UNAUTHENTICATED" in upper_error
            or "INVALID API KEY" in upper_error
        ):

            user_error = (
                "Gemini API key is invalid. "
                "Check your GEMINI_API_KEY and restart Django."
            )

        else:

            user_error = (
                "Quiz AI error: "
                + type(error).__name__
                + " - "
                + error_text
            )

        return JsonResponse({
            "success": False,
            "error": user_error
        }, status=500)


# =========================================================
# QUIZ AI SUBMIT
# =========================================================

@require_GET
def quiz_history_api(request):
    return JsonResponse({
        "success": True,
        "history": []
    })


@require_POST
def quiz_ai_submit(request):

    try:

        data = json.loads(request.body)

        questions = data.get("questions", [])
        answers = data.get("answers", [])

        if not questions:

            return JsonResponse({
                "success": False,
                "error": "No quiz questions were submitted."
            }, status=400)

        if not isinstance(questions, list):

            return JsonResponse({
                "success": False,
                "error": "Invalid questions data."
            }, status=400)

        if not isinstance(answers, list):

            return JsonResponse({
                "success": False,
                "error": "Invalid answers data."
            }, status=400)

        score = 0
        answer_key = []

        for index, question in enumerate(questions):

            if not isinstance(question, dict):
                continue

            selected = ""

            if index < len(answers):
                selected = str(
                    answers[index] or ""
                ).strip().upper()

            correct = str(
                question.get("correct", "")
            ).strip().upper()

            is_correct = (
                selected != ""
                and selected == correct
            )

            if is_correct:
                score += 1

            answer_key.append({
                "question_number": index + 1,
                "question": question.get(
                    "question",
                    ""
                ),
                "selected": selected,
                "correct": correct,
                "is_correct": is_correct,
                "explanation": question.get(
                    "explanation",
                    "No explanation available."
                ),
                "hint": question.get(
                    "hint",
                    ""
                ),
                "options": question.get(
                    "options",
                    []
                )
            })

        total = len(questions)

        percentage = 0

        if total > 0:
            percentage = round(
                (score / total) * 100
            )

        # XP calculation
        xp_earned = score * 10

        if percentage == 100:
            xp_earned += 20

        elif percentage >= 80:
            xp_earned += 10

        elif percentage >= 60:
            xp_earned += 5

        if percentage >= 80:
            performance = "Excellent"

        elif percentage >= 60:
            performance = "Good"

        elif percentage >= 40:
            performance = "Needs Improvement"

        else:
            performance = "Keep Practicing"

        return JsonResponse({
            "success": True,
            "score": score,
            "total": total,
            "percentage": percentage,
            "xp_earned": xp_earned,
            "performance": performance,
            "answer_key": answer_key,
            "message": "Quiz completed successfully!"
        })

    except json.JSONDecodeError:

        return JsonResponse({
            "success": False,
            "error": "Invalid quiz submission data."
        }, status=400)

    except Exception as error:

        print("=" * 60)
        print("QUIZ AI SUBMIT ERROR")
        print("ERROR TYPE:", type(error).__name__)
        print("ERROR:", str(error))
        print("=" * 60)

        return JsonResponse({
            "success": False,
            "error": (
                "Unable to submit the quiz. "
                "Please try again."
            )
        }, status=500)


# =========================================================
# TRANSLATION
# =========================================================

@require_GET
def translate_text(request):

    text = request.GET.get("text", "").strip()
    source = request.GET.get("source", "")
    target = request.GET.get("target", "")

    if not text:

        return JsonResponse({
            "success": False,
            "error": "Please enter some text."
        })

    language_codes = {
        "English": "en",
        "Tamil": "ta",
        "Hindi": "hi",
        "French": "fr",
        "German": "de",
        "Spanish": "es",
        "Japanese": "ja"
    }

    source_code = language_codes.get(source)
    target_code = language_codes.get(target)

    if not source_code or not target_code:

        return JsonResponse({
            "success": False,
            "error": "Selected language is not supported."
        })

    if source_code == target_code:

        return JsonResponse({
            "success": True,
            "translation": text
        })

    try:

        url = (
            "https://api.mymemory.translated.net/get"
            "?q=" + quote(text)
            + "&langpair="
            + source_code
            + "|"
            + target_code
        )

        request_api = Request(
            url,
            headers={
                "User-Agent": "SmartLearn/1.0"
            }
        )

        with urlopen(
            request_api,
            timeout=15
        ) as response:

            data = json.loads(
                response.read().decode("utf-8")
            )

        translated_text = (
            data
            .get("responseData", {})
            .get("translatedText")
        )

        if not translated_text:

            return JsonResponse({
                "success": False,
                "error": "Translation was not found."
            })

        return JsonResponse({
            "success": True,
            "translation": translated_text
        })

    except Exception as error:

        print("Translation error:", error)

        return JsonResponse({
            "success": False,
            "error": (
                "Unable to translate right now. "
                "Please check your internet connection."
            )
        })


# =========================================================
# SUMMARY AI PAGE
# =========================================================

def summary_ai(request):

    return render(
        request,
        "summary_ai.html"
    )


# =========================================================
# SUMMARY AI API
# =========================================================

@require_POST
def summary_ai_api(request):

    action = request.POST.get(
        "action",
        "analyze"
    )

    material = request.POST.get(
        "material",
        ""
    ).strip()

    question = request.POST.get(
        "question",
        ""
    ).strip()

    level = request.POST.get(
        "level",
        "Beginner"
    )

    language = request.POST.get(
        "language",
        "English"
    )

    if not material:

        return JsonResponse({
            "success": False,
            "error": "Please enter your study material first."
        })

    if action == "analyze":

        prompt = f"""
You are Summary AI inside SmartLearn LMS.

Analyze the following study material.

Student level:
{level}

Preferred explanation language:
{language}

Study material:
{material}

Give the response in this exact structure:

SMART SUMMARY:
Give a clear and useful summary.

KEY CONCEPTS:
1. Concept
2. Concept
3. Concept
4. Concept
5. Concept

IMPORTANT DEFINITIONS:
List important definitions.

Keep the explanation suitable for the student's level.
"""

    elif action == "doubt":

        prompt = f"""
You are Summary AI inside SmartLearn LMS.

The student is studying this material:

{material}

Student level:
{level}

Preferred language:
{language}

Student question:

{question}

Answer the question clearly.

Include:

1. Direct answer
2. Simple explanation
3. Step-by-step explanation if useful
4. One real-life example

Do not ignore the study material.
"""

    elif action == "simplify":

        prompt = f"""
You are Summary AI inside SmartLearn LMS.

Study material:

{material}

Student level:

{level}

Explain the material in the simplest possible way.

Use:

- very simple words
- short sentences
- easy examples
- important points

Preferred language:
{language}
"""

    elif action == "practice":

        prompt = f"""
You are Summary AI inside SmartLearn LMS.

Study material:

{material}

Create practice questions for the student.

Student level:
{level}

Create:

1. One easy question
2. One medium question
3. One application question
4. Answers with explanations

Preferred language:
{language}
"""

    elif action == "exam":

        prompt = f"""
You are Summary AI inside SmartLearn LMS.

Study material:

{material}

Create an exam revision guide.

Include:

IMPORTANT FOR EXAM:

1. Most important concepts
2. Important definitions
3. Important points to remember
4. Possible exam questions
5. Quick revision section

Student level:
{level}

Preferred language:
{language}
"""

    elif action == "connect":

        prompt = f"""
You are Summary AI inside SmartLearn LMS.

Study material:

{material}

Explain how the concepts in this material are connected.

Show:

1. Main concept
2. Related concepts
3. How they are connected
4. A simple real-life example

Student level:
{level}

Preferred language:
{language}
"""

    elif action == "step":

        prompt = f"""
You are Summary AI inside SmartLearn LMS.

Study material:

{material}

Break the topic into small steps.

Explain each step clearly.

Student level:
{level}

Preferred language:
{language}
"""

    else:

        prompt = f"""
You are Summary AI inside SmartLearn LMS.

Study material:

{material}

Student level:
{level}

Preferred language:
{language}

Explain the study material clearly and simply.
"""

    try:

        client = get_gemini_client()

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        answer = response.text

        if not answer:

            return JsonResponse({
                "success": False,
                "error": "AI returned an empty response."
            })

        return JsonResponse({
            "success": True,
            "answer": answer
        })

    except Exception as error:

        print("=" * 60)
        print("SUMMARY AI ERROR")
        print(error)
        print("=" * 60)

        error_text = str(error).upper()

        # =====================================================
        # GEMINI QUOTA FALLBACK
        # =====================================================

        if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:

            sentences = [
                sentence.strip()
                for sentence in material.replace("\n", " ").split(".")
                if sentence.strip()
            ]

            if len(sentences) > 5:
                sentences = sentences[:5]

            local_summary = "\n\n".join(
                f"• {sentence}."
                for sentence in sentences
            )

            return JsonResponse({
                "success": True,
                "answer": (
                    "📚 SUMMARY\n\n"
                    "Gemini AI quota is currently unavailable, "
                    "so SmartLearn created a basic summary from "
                    "your study material.\n\n"
                    f"{local_summary}"
                ),
                "fallback": True
            })

        return JsonResponse({
            "success": False,
            "error": (
                "Unable to generate the summary right now. "
                "Please try again."
            )
        }, status=500)


# =========================================================
# NOTES AI API
# =========================================================

@require_POST
def notes_ai_api(request):

    material = request.POST.get(
        "material",
        ""
    ).strip()

    style = request.POST.get(
        "style",
        "Detailed Notes"
    )

    language = request.POST.get(
        "language",
        "English"
    )

    if not material:

        return JsonResponse({
            "success": False,
            "error": "Please enter your study material."
        })

    prompt = f"""
You are Notes AI inside SmartLearn LMS.

Your job is to convert study material into
clear, organized and useful study notes.

Study material:
{material}

Note style:
{style}

Output language:
{language}

Create structured notes.

Use the following structure when appropriate:

TITLE

📌 Definition

🎯 Key Concepts

📝 Important Points

💡 Examples

⚠️ Important Things to Remember

📚 Exam Points

Do not invent information that is not supported
by the study material.

Keep the notes easy to read and useful for
later revision.

Do not write an introduction about yourself.

Give only the study notes.
"""

    try:

        client = get_gemini_client()

        models_to_try = [
            "gemini-3.8-flash",
            "gemini-3.7-flash",
            "gemini-3.6-flash",
            "gemini-3.5-flash",
        ]

        response = None
        last_error = None

        for model_name in models_to_try:

            try:

                print("=" * 60)
                print("NOTES AI USING MODEL:", model_name)
                print("=" * 60)

                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )

                if response and response.text:

                    print(
                        "NOTES AI SUCCESS:",
                        model_name
                    )

                    break

            except Exception as model_error:

                last_error = model_error

                print("=" * 60)
                print(
                    "NOTES AI MODEL FAILED:",
                    model_name
                )
                print(model_error)
                print("=" * 60)

                continue

        if response is None or not response.text:

            return JsonResponse({
                "success": False,
                "error": (
                    "Notes AI is temporarily unavailable. "
                    "Please try again in a few seconds."
                )
            })

        notes = response.text

        if not notes:

            return JsonResponse({
                "success": False,
                "error": "AI returned empty notes."
            })

        return JsonResponse({
            "success": True,
            "notes": notes
        })

    except Exception as error:

        print("=" * 60)
        print("NOTES AI ERROR")
        print(error)
        print("=" * 60)

        return JsonResponse({
            "success": False,
            "error": str(error)
        })


# =========================================================
# ADAPTIVE AI PAGE
# =========================================================

def adaptive_ai(request):

    return render(
        request,
        "adaptive_ai.html"
    )


# =========================================================
# ADAPTIVE AI API
# =========================================================

@require_POST
def adaptive_ai_api(request):

    subject = request.POST.get(
        "subject",
        ""
    ).strip()

    level = request.POST.get(
        "level",
        "Beginner"
    )

    score = request.POST.get(
        "score",
        ""
    ).strip()

    weak_topics = request.POST.get(
        "weak_topics",
        ""
    ).strip()

    if not subject:

        return JsonResponse({
            "success": False,
            "error": "Please enter a subject."
        })

    if not score:

        return JsonResponse({
            "success": False,
            "error": "Please enter your quiz score."
        })

    prompt = f"""
You are Adaptive AI inside SmartLearn LMS.

Your job is to create a personalized learning plan
for the student.

Subject:
{subject}

Student level:
{level}

Recent quiz score:
{score}%

Difficult topics:
{weak_topics}

Analyze the student's learning situation.

Give the response using this structure:

📊 LEARNING ANALYSIS

Explain what the score and level indicate.

🎯 PERSONALIZED LEARNING PATH

Give a suitable learning path.

🔍 TOPICS TO IMPROVE

Identify topics that should receive more attention.

📚 WHAT TO REVISE

Suggest topics for revision.

📈 DIFFICULTY RECOMMENDATION

Explain whether the student should use
easier, similar, or more advanced material.

🚀 WHAT TO LEARN NEXT

Give the next recommended topic.

💡 STUDY TIPS

Give practical study suggestions.

Keep the explanation simple and useful.

Do not invent information about the student's
performance beyond the information provided.
"""

    models = [
        "gemini-3.8-flash",
        "gemini-3.5-flash-lite"
    ]

    last_error = None

    for model_name in models:

        for attempt in range(3):

            try:

                client = get_gemini_client()

                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )

                answer = response.text

                if not answer:

                    return JsonResponse({
                        "success": False,
                        "error": "AI returned an empty response."
                    })

                return JsonResponse({
                    "success": True,
                    "answer": answer
                })

            except Exception as error:

                last_error = error

                print("=" * 60)
                print("ADAPTIVE AI ERROR")
                print("MODEL:", model_name)
                print("ATTEMPT:", attempt + 1)
                print(error)
                print("=" * 60)

                error_text = str(error)

                if (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text
                    or "429" in error_text
                    or "RESOURCE_EXHAUSTED" in error_text
                ):

                    time.sleep(2 ** attempt)

                    continue

                break

    return JsonResponse({
        "success": False,
        "error": (
            "Gemini is temporarily unavailable. "
            "Adaptive AI tried multiple models. "
            "Please try again in a few seconds."
        )
    })


# =========================================================
# TUTOR AI PAGE
# =========================================================

def tutor_ai(request):

    return render(
        request,
        "tutor_ai.html"
    )


# =========================================================
# TUTOR AI API
# =========================================================

@require_POST
def tutor_ai_api(request):

    question = request.POST.get(
        "question",
        ""
    ).strip()

    conversation_text = request.POST.get(
        "conversation",
        ""
    )

    if not question:

        return JsonResponse({
            "success": False,
            "error": "Please ask a question."
        })

    prompt = f"""
You are Robert, the friendly AI Tutor
inside SmartLearn LMS.

Your job is to teach students clearly.

Previous conversation:
{conversation_text}

New student question:
{question}

Teaching rules:

1. Explain clearly.
2. Use simple language.
3. Explain difficult topics step by step.
4. Give an example when useful.
5. Do not invent information.
6. If the student is confused,
   explain the topic more simply.
7. Be friendly and encouraging.
8. If the question is about programming,
   give a simple programming example.
9. Answer the student's actual question.
10. Do not introduce yourself again.

Give only the answer to the student.
"""

    models = [
        "gemini-3.8-flash",
        "gemini-3.5-flash-lite"
    ]

    last_error = None

    for model_name in models:

        for attempt in range(3):

            try:

                client = get_gemini_client()

                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )

                answer = response.text

                if not answer:

                    return JsonResponse({
                        "success": False,
                        "error": "AI returned an empty answer."
                    })

                return JsonResponse({
                    "success": True,
                    "answer": answer
                })

            except Exception as error:

                last_error = error

                print("=" * 60)
                print("TUTOR AI ERROR")
                print("MODEL:", model_name)
                print("ATTEMPT:", attempt + 1)
                print(error)
                print("=" * 60)

                error_text = str(error)

                if (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text
                    or "429" in error_text
                    or "RESOURCE_EXHAUSTED" in error_text
                ):

                    time.sleep(2 ** attempt)

                    continue

                break

    return JsonResponse({
        "success": False,
        "error": (
            "Gemini is temporarily unavailable. "
            "Please try again in a few seconds."
        )
    })


# =========================================================
# GAMIFICATION PAGE
# =========================================================

def gamification(request):

    return render(
        request,
        "gamification.html"
    )


# ============================================================
# GAMIFICATION + QUIZ HISTORY
# ADD THIS AT THE BOTTOM OF accounts/views.py
# ============================================================

from django.views.decorators.http import require_GET, require_POST
from django.http import JsonResponse
import json
from datetime import date


# ============================================================
# QUIZ HISTORY API
# ============================================================

@require_GET
def quiz_history_api(request):

    try:

        history = request.session.get(
            "quiz_history",
            []
        )

        if not isinstance(history, list):
            history = []

        return JsonResponse({
            "success": True,
            "history": history,
            "total_quizzes": len(history)
        })

    except Exception as error:

        print("=" * 60)
        print("QUIZ HISTORY ERROR")
        print("ERROR:", str(error))
        print("=" * 60)

        return JsonResponse({
            "success": False,
            "error": "Unable to load quiz history."
        }, status=500)


# ============================================================
# GAMIFICATION DATA API
# ============================================================

@require_GET
def gamification_api(request):

    try:

        history = request.session.get(
            "quiz_history",
            []
        )

        if not isinstance(history, list):
            history = []

        total_xp = 0
        total_quizzes = len(history)
        total_correct = 0
        total_questions = 0

        for item in history:

            total_xp += int(
                item.get("xp_earned", 0)
            )

            total_correct += int(
                item.get("score", 0)
            )

            total_questions += int(
                item.get("total", 0)
            )

        # ----------------------------------------------------
        # LEVEL
        # ----------------------------------------------------

        level = (total_xp // 500) + 1

        current_level_xp = total_xp % 500

        next_level_xp = 500

        level_percentage = round(
            (current_level_xp / next_level_xp) * 100
        )

        if level_percentage > 100:
            level_percentage = 100

        # ----------------------------------------------------
        # LEVEL TITLE
        # ----------------------------------------------------

        if level == 1:
            level_title = "Beginner Explorer"

        elif level == 2:
            level_title = "Curious Learner"

        elif level == 3:
            level_title = "Knowledge Seeker"

        elif level == 4:
            level_title = "Smart Learner"

        elif level == 5:
            level_title = "Knowledge Explorer"

        elif level >= 10:
            level_title = "Master Mind"

        else:
            level_title = "Learning Champion"

        # ----------------------------------------------------
        # AVERAGE SCORE
        # ----------------------------------------------------

        if total_questions > 0:

            average_score = round(
                (total_correct / total_questions) * 100
            )

        else:

            average_score = 0

        # ----------------------------------------------------
        # BADGES
        # ----------------------------------------------------

        badges = []

        if total_quizzes >= 1:

            badges.append({
                "icon": "🌟",
                "name": "First Step",
                "description": "Completed your first quiz."
            })

        if total_quizzes >= 5:

            badges.append({
                "icon": "🧠",
                "name": "Quick Learner",
                "description": "Completed 5 quizzes."
            })

        if average_score >= 80:

            badges.append({
                "icon": "🎯",
                "name": "Quiz Master",
                "description": "Maintained an average score above 80%."
            })

        if total_xp >= 1000:

            badges.append({
                "icon": "🚀",
                "name": "Fast Progress",
                "description": "Earned 1,000 XP."
            })

        if total_xp >= 2500:

            badges.append({
                "icon": "💎",
                "name": "Diamond Learner",
                "description": "Earned 2,500 XP."
            })

        if total_correct >= 25:

            badges.append({
                "icon": "🏆",
                "name": "Knowledge Champion",
                "description": "Answered 25 questions correctly."
            })

        # ----------------------------------------------------
        # STREAK
        # ----------------------------------------------------

        streak = request.session.get(
            "learning_streak",
            0
        )

        # ----------------------------------------------------
        # DAILY GOAL
        # ----------------------------------------------------

        today = date.today().isoformat()

        daily_data = request.session.get(
            "daily_learning",
            {}
        )

        if daily_data.get("date") != today:

            daily_data = {
                "date": today,
                "questions": 0
            }

        daily_questions = int(
            daily_data.get("questions", 0)
        )

        daily_goal = 10

        daily_percentage = round(
            min(
                (daily_questions / daily_goal) * 100,
                100
            )
        )

        return JsonResponse({

            "success": True,

            "total_xp": total_xp,

            "level": level,

            "level_title": level_title,

            "current_level_xp": current_level_xp,

            "next_level_xp": next_level_xp,

            "level_percentage": level_percentage,

            "streak": streak,

            "badges": badges,

            "badge_count": len(badges),

            "total_quizzes": total_quizzes,

            "average_score": average_score,

            "total_correct": total_correct,

            "total_questions": total_questions,

            "daily_questions": daily_questions,

            "daily_goal": daily_goal,

            "daily_percentage": daily_percentage,

            "recent_history": history[-5:][::-1]

        })

    except Exception as error:

        print("=" * 60)
        print("GAMIFICATION API ERROR")
        print("ERROR:", str(error))
        print("=" * 60)

        return JsonResponse({
            "success": False,
            "error": "Unable to load gamification data."
        }, status=500)


# ============================================================
# KNOWLEDGE QUEST
# ============================================================

@require_GET
def knowledge_quest_api(request):

    questions = [

        {
            "question": "Which keyword is used to define a function in Python?",
            "options": [
                "function",
                "def",
                "fun",
                "define"
            ],
            "answer": "B",
            "explanation": "Python uses the def keyword to define a function."
        },

        {
            "question": "Which data type is used to store True or False?",
            "options": [
                "String",
                "Integer",
                "Boolean",
                "List"
            ],
            "answer": "C",
            "explanation": "Boolean values represent True or False."
        },

        {
            "question": "Which symbol is used for comments in Python?",
            "options": [
                "//",
                "#",
                "/*",
                "--"
            ],
            "answer": "B",
            "explanation": "Python uses # for single-line comments."
        },

        {
            "question": "Which function displays output in Python?",
            "options": [
                "show()",
                "display()",
                "print()",
                "output()"
            ],
            "answer": "C",
            "explanation": "The print() function displays output."
        },

        {
            "question": "Which collection is ordered and changeable?",
            "options": [
                "Tuple",
                "List",
                "Set",
                "Dictionary"
            ],
            "answer": "B",
            "explanation": "Python lists are ordered and mutable."
        }

    ]

    return JsonResponse({
        "success": True,
        "questions": questions
    })


# ============================================================
# SUBMIT KNOWLEDGE QUEST
# ============================================================

@require_POST
def knowledge_quest_submit(request):

    try:

        data = json.loads(request.body)

        answers = data.get(
            "answers",
            []
        )

        questions = [

            {
                "answer": "B",
                "explanation":
                    "Python uses the def keyword to define a function."
            },

            {
                "answer": "C",
                "explanation":
                    "Boolean values represent True or False."
            },

            {
                "answer": "B",
                "explanation":
                    "Python uses # for single-line comments."
            },

            {
                "answer": "C",
                "explanation":
                    "The print() function displays output."
            },

            {
                "answer": "B",
                "explanation":
                    "Python lists are ordered and mutable."
            }

        ]

        score = 0

        results = []

        for index, question in enumerate(questions):

            selected = ""

            if index < len(answers):

                selected = str(
                    answers[index]
                ).upper()

            correct = question["answer"]

            is_correct = (
                selected == correct
            )

            if is_correct:

                score += 1

            results.append({

                "question_number": index + 1,

                "selected": selected,

                "correct": correct,

                "is_correct": is_correct,

                "explanation":
                    question["explanation"]

            })

        total = len(questions)

        percentage = round(
            (score / total) * 100
        )

        # ----------------------------------------------------
        # XP SYSTEM
        # ----------------------------------------------------

        xp_earned = score * 20

        if percentage == 100:

            xp_earned += 50

        elif percentage >= 80:

            xp_earned += 30

        elif percentage >= 60:

            xp_earned += 15

        # ----------------------------------------------------
        # SAVE QUIZ HISTORY
        # ----------------------------------------------------

        history = request.session.get(
            "quiz_history",
            []
        )

        if not isinstance(history, list):

            history = []

        history.append({

            "subject": "Knowledge Quest",

            "topic": "Python",

            "score": score,

            "total": total,

            "percentage": percentage,

            "xp_earned": xp_earned,

            "date": date.today().isoformat()

        })

        # Keep last 50 attempts

        history = history[-50:]

        request.session["quiz_history"] = history

        # ----------------------------------------------------
        # DAILY PROGRESS
        # ----------------------------------------------------

        today = date.today().isoformat()

        daily_data = request.session.get(
            "daily_learning",
            {}
        )

        if daily_data.get("date") != today:

            daily_data = {

                "date": today,

                "questions": 0

            }

        daily_data["questions"] = (

            int(
                daily_data.get(
                    "questions",
                    0
                )
            )

            + total

        )

        request.session["daily_learning"] = daily_data

        # ----------------------------------------------------
        # STREAK
        # ----------------------------------------------------

        streak = request.session.get(
            "learning_streak",
            0
        )

        streak += 1

        request.session["learning_streak"] = streak

        request.session.modified = True

        return JsonResponse({

            "success": True,

            "score": score,

            "total": total,

            "percentage": percentage,

            "xp_earned": xp_earned,

            "results": results,

            "streak": streak,

            "message":
                "Knowledge Quest completed!"

        })

    except Exception as error:

        print("=" * 60)
        print("KNOWLEDGE QUEST SUBMIT ERROR")
        print("ERROR:", str(error))
        print("=" * 60)

        return JsonResponse({

            "success": False,

            "error":
                "Unable to submit Knowledge Quest."

        }, status=500)


# =========================================================
# QUIZ AI API
# =========================================================

@require_POST
def quiz_ai_api(request):

    # YOUR COMPLETE EXISTING quiz_ai_api CODE
    # DO NOT CHANGE IT

    ...


# =========================================================
# QUIZ HISTORY API
# =========================================================

def quiz_history_api(request):

    # quiz history code goes here

    return JsonResponse({
        "success": True,
        "history": []
    })


# =========================================================
# GAMIFICATION
# =========================================================

def gamification(request):

    return render(
        request,
        "gamification.html"
    )


# =========================================================
# VOICE AI API
# =========================================================

@require_POST
def voice_ai_api(request):

    try:

        data = json.loads(request.body)

        message = data.get(
            "message",
            ""
        ).strip()

        language = data.get(
            "language",
            "en-IN"
        )

        if not message:

            return JsonResponse({
                "success": False,
                "error": "Please enter a question."
            }, status=400)

        client = get_gemini_client()

        language_name = {
            "en-IN": "English",
            "ta-IN": "Tamil",
            "hi-IN": "Hindi"
        }.get(language, "English")

        prompt = f"""
You are SmartLearn Voice AI, a friendly educational assistant.

The student is asking a question using voice.

Answer in {language_name}.

Student question:
{message}

Give a clear, beginner-friendly educational answer.
Keep the answer easy to understand.
Do not use unnecessary complicated words.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        answer = response.text.strip()

        return JsonResponse({
            "success": True,
            "answer": answer
        })

    except json.JSONDecodeError:

        return JsonResponse({
            "success": False,
            "error": "Invalid request data."
        }, status=400)

    except Exception as error:

        print("=" * 60)
        print("VOICE AI ERROR")
        print("ERROR TYPE:", type(error).__name__)
        print("ERROR:", str(error))
        print("=" * 60)

        return JsonResponse({
            "success": False,
            "error": "Unable to connect to Voice AI."
        }, status=500)


# =========================================================
# LEARNTWIN AI PAGE
# =========================================================

def learntwin(request):

    return render(
        request,
        "learntwin.html"
    )


# =========================================================
# LEARNTWIN AI API
# =========================================================

@require_POST
def learntwin_api(request):

    try:

        data = json.loads(request.body)

        name = data.get(
            "name",
            "Student"
        ).strip()

        subject = data.get(
            "subject",
            "Python"
        ).strip()

        level = data.get(
            "level",
            "Beginner"
        ).strip()

        score = data.get(
            "score",
            0
        )

        weak_topics = data.get(
            "weak_topics",
            ""
        ).strip()

        completed_topics = data.get(
            "completed_topics",
            ""
        ).strip()

        streak = data.get(
            "streak",
            0
        )

        if not subject:

            return JsonResponse({
                "success": False,
                "error": "Please enter a subject."
            }, status=400)

        # =====================================================
        # LEARNTWIN PROMPT
        # =====================================================

        prompt = f"""
You are LearnTwin AI inside SmartLearn LMS.

LearnTwin is the student's personal AI learning twin.

Your job is NOT to act like a normal chatbot.

Instead, create a learning profile of the student
and understand how the student is progressing.

Student name:
{name}

Subject:
{subject}

Current level:
{level}

Recent quiz score:
{score}%

Weak topics:
{weak_topics}

Completed topics:
{completed_topics}

Learning streak:
{streak} days

Create a personalized LearnTwin report.

Use exactly this structure:

🧠 MY LEARNING TWIN

Give a short description of the student's current
learning profile.

📊 LEARNING PROFILE

Describe the student's current learning level.

💪 STRENGTHS

List the student's likely strengths based only on
the information provided.

🔍 WEAK AREAS

Identify areas that need more practice.

🎯 PERSONAL LEARNING GOAL

Give one realistic learning goal.

📚 NEXT BEST TOPIC

Recommend the next topic to study.

⚡ CHALLENGE LEVEL

Recommend Beginner, Intermediate, or Advanced.

🗺️ 7-DAY LEARNING PATH

Give a simple 7-day learning plan.

🤖 TWIN MESSAGE

Give one short motivational message from the
student's LearnTwin.

Rules:

1. Do not invent achievements.
2. Do not claim information that was not provided.
3. Keep the explanation beginner-friendly.
4. Make the recommendations practical.
5. Use the student's score and weak topics.
6. Make the LearnTwin feel personalized.
"""

        # =====================================================
        # GEMINI
        # =====================================================

        client = get_gemini_client()

        models = [
            "gemini-3.8-flash",
            "gemini-3.5-flash-lite"
        ]

        last_error = None

        for model_name in models:

            try:

                print("=" * 60)
                print("LEARN TWIN USING MODEL:", model_name)
                print("=" * 60)

                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )

                if response and response.text:

                    answer = response.text.strip()

                    return JsonResponse({
                        "success": True,
                        "answer": answer
                    })

            except Exception as error:

                last_error = error

                print("=" * 60)
                print("LEARN TWIN MODEL ERROR")
                print("MODEL:", model_name)
                print("ERROR:", str(error))
                print("=" * 60)

                error_text = str(error).upper()

                if (
                    "429" in error_text
                    or "RESOURCE_EXHAUSTED" in error_text
                    or "503" in error_text
                    or "UNAVAILABLE" in error_text
                ):

                    time.sleep(2)

                    continue

                break

        # =====================================================
        # ERROR RESPONSE
        # =====================================================

        return JsonResponse({
            "success": False,
            "error": (
                "LearnTwin AI is temporarily unavailable. "
                "Please try again later."
            )
        }, status=503)

    except json.JSONDecodeError:

        return JsonResponse({
            "success": False,
            "error": "Invalid LearnTwin request data."
        }, status=400)

    except Exception as error:

        print("=" * 60)
        print("LEARN TWIN ERROR")
        print("ERROR TYPE:", type(error).__name__)
        print("ERROR:", str(error))
        print("=" * 60)

        return JsonResponse({
            "success": False,
            "error": (
                "Unable to create your LearnTwin profile."
            )
        }, status=500)


# =========================================================
# LEARNTWIN
# =========================================================

def learntwin(request):

    return render(request, "learntwin.html")


# =========================================================
# LEARNTWIN API
# =========================================================

@require_POST
def learntwin_api(request):

    try:

        data = json.loads(request.body)

        goal = data.get(
            "goal",
            ""
        ).strip()

        skill_level = data.get(
            "skill_level",
            "Beginner"
        )

        study_time = data.get(
            "study_time",
            "30 minutes"
        )

        quiz_score = int(
            data.get(
                "quiz_score",
                60
            )
        )

        confidence = data.get(
            "confidence",
            "Medium"
        )

        weak_topic = data.get(
            "weak_topic",
            ""
        ).strip()

        if not goal:

            return JsonResponse({
                "success": False,
                "error": "Please enter your learning goal."
            }, status=400)

        # -------------------------------------------------
        # READINESS SCORE
        # -------------------------------------------------

        readiness = quiz_score

        if confidence == "High":

            readiness += 8

        elif confidence == "Medium":

            readiness += 4

        if skill_level == "Intermediate":

            readiness += 5

        elif skill_level == "Advanced":

            readiness += 8

        if study_time == "1 hour":

            readiness += 4

        elif study_time == "2 hours":

            readiness += 7

        elif study_time == "3+ hours":

            readiness += 10

        readiness = max(
            0,
            min(
                100,
                readiness
            )
        )

        # -------------------------------------------------
        # GEMINI
        # -------------------------------------------------

        client = get_gemini_client()

        prompt = f"""
You are LearnTwin, a personal learning digital twin inside
an educational LMS.

Create a useful learning profile for this student.

Learning goal:
{goal}

Skill level:
{skill_level}

Daily study time:
{study_time}

Recent quiz score:
{quiz_score}%

Confidence:
{confidence}

Weak topic:
{weak_topic if weak_topic else "Not specified"}

Return ONLY valid JSON.

Use exactly these keys:

twin_title
description
strengths
risks
strategy
next_action
daily_plan
consistency

Keep every value short and beginner-friendly.

Do not use markdown.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text.strip()

        # -------------------------------------------------
        # CLEAN GEMINI RESPONSE
        # -------------------------------------------------

        if text.startswith("```"):

            text = text.replace(
                "```json",
                ""
            )

            text = text.replace(
                "```",
                ""
            )

            text = text.strip()

        result = json.loads(text)

        return JsonResponse({

            "success": True,

            "twin_title":
                result.get(
                    "twin_title",
                    "Your Learning Twin"
                ),

            "description":
                result.get(
                    "description",
                    "Your learning profile is ready."
                ),

            "readiness":
                readiness,

            "strengths":
                result.get(
                    "strengths",
                    "You are actively building your skills."
                ),

            "risks":
                result.get(
                    "risks",
                    "Review weak areas regularly."
                ),

            "strategy":
                result.get(
                    "strategy",
                    "Study in short focused sessions."
                ),

            "next_action":
                result.get(
                    "next_action",
                    "Practice your weakest topic."
                ),

            "daily_plan":
                result.get(
                    "daily_plan",
                    "Study, practice, review and test yourself."
                ),

            "consistency":
                result.get(
                    "consistency",
                    "Study consistently every day."
                )

        })

    except Exception as error:

        print("=" * 60)
        print("LEARN TWIN ERROR")
        print("ERROR TYPE:", type(error).__name__)
        print("ERROR:", str(error))
        print("=" * 60)

        # =================================================
        # LOCAL FALLBACK
        # =================================================

        error_text = str(error).upper()

        if (
            "429" in error_text
            or
            "RESOURCE_EXHAUSTED" in error_text
        ):

            if quiz_score >= 80:

                twin_title = "Strong Learner"

            elif quiz_score >= 60:

                twin_title = "Growing Learner"

            else:

                twin_title = "Needs More Practice"

            if confidence == "High":

                strength = (
                    "Your confidence is strong and "
                    "can help you learn independently."
                )

            elif confidence == "Medium":

                strength = (
                    "You have a developing learning "
                    "foundation."
                )

            else:

                strength = (
                    "You are identifying areas where "
                    "your confidence can improve."
                )

            if weak_topic:

                risk = (
                    f"Your main risk area is "
                    f"{weak_topic}. Give this topic "
                    f"extra practice."
                )

                next_action = (
                    f"Spend your next study session "
                    f"practicing {weak_topic}."
                )

            else:

                risk = (
                    "Your weak topic has not been "
                    "identified yet."
                )

                next_action = (
                    "Take a short practice quiz to "
                    "identify your weakest topic."
                )

            if study_time == "15 minutes":

                daily_plan = (
                    "5 min revision → "
                    "7 min practice → "
                    "3 min self-test."
                )

            elif study_time == "30 minutes":

                daily_plan = (
                    "10 min revision → "
                    "15 min practice → "
                    "5 min self-test."
                )

            elif study_time == "1 hour":

                daily_plan = (
                    "15 min revision → "
                    "30 min practice → "
                    "15 min testing."
                )

            else:

                daily_plan = (
                    "20 min revision → "
                    "40 min focused practice → "
                    "20 min testing → "
                    "10 min review."
                )

            return JsonResponse({

                "success": True,

                "twin_title":
                    twin_title,

                "description":
                    (
                        f"Your Learning Twin shows that "
                        f"you are working toward {goal}. "
                        f"Your current quiz performance "
                        f"is {quiz_score}%."
                    ),

                "readiness":
                    readiness,

                "strengths":
                    strength,

                "risks":
                    risk,

                "strategy":
                    (
                        f"As a {skill_level.lower()} "
                        f"learner, use focused practice "
                        f"and review your mistakes."
                    ),

                "next_action":
                    next_action,

                "daily_plan":
                    daily_plan,

                "consistency":
                    (
                        "Keep a regular study routine. "
                        "Small daily progress is better "
                        "than studying only before exams."
                    ),

                "fallback":
                    True

            })

        return JsonResponse({

            "success": False,

            "error":
                "Unable to create your Learning Twin right now."

        }, status=500)

def register_student(request):
    if request.method == "POST":
        form = StudentRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your student account is ready!")
            return redirect("student_home")
    else:
        form = StudentRegistrationForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form},
    )

def scorm_catalogue(request):
    courses = ScormCourse.objects.all().order_by("-created_at")
    return render(request, "scorm_courses.html")

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(
            request,
            data=request.POST,
        )

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if user.is_staff or user.groups.filter(
                name="Instructors"
            ).exists():
                return redirect("instructor_home")

            return redirect("student_home")
    else:
        form = AuthenticationForm(request)

    return render(
        request,
        "accounts/login.html",
        {"form": form},
    )


@login_required
def student_home(request):
    if request.user.is_staff or request.user.groups.filter(
        name="Instructors"
    ).exists():
        return redirect("instructor_home")

    return render(request, "accounts/student_home.html")


@login_required
def instructor_home(request):
    if not (
        request.user.is_staff
        or request.user.groups.filter(name="Instructors").exists()
    ):
        messages.error(request, "Instructor access is required.")
        return redirect("student_home")

    return render(request, "accounts/instructor_home.html")


@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, "You have logged out.")
    return redirect("login")
@login_required
def upload_scorm_course(request):

    # Only instructors and staff can upload courses
    is_instructor = (
        request.user.is_staff
        or request.user.groups.filter(name="Instructors").exists()
    )

    if not is_instructor:
        messages.error(
            request,
            "Only authorized instructors can upload SCORM courses."
        )
        return redirect("scorm_catalogue")

    if request.method == "POST":
        form = ScormCourseForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            course = form.save(commit=False)
            course.uploaded_by = request.user
            course.save()

            messages.success(
                request,
                "SCORM course uploaded successfully!"
            )

            return redirect("scorm_catalogue")

    else:
        form = ScormCourseForm()

    return render(
        request,
        "accounts/scorm_upload.html",
        {"form": form}
    )