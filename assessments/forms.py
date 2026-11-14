
from django import forms
from .models import Assessment, Question


# ==========================================
# 1. ASSESSMENT CREATION FORM
# ==========================================

class AssessmentForm(forms.ModelForm):

    start_date = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            format="%Y-%m-%dT%H:%M",
            attrs={
                "type": "datetime-local",
                "class": "form-control"
            }
        )
    )

    end_date = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            format="%Y-%m-%dT%H:%M",
            attrs={
                "type": "datetime-local",
                "class": "form-control"
            }
        )
    )

    class Meta:
        model = Assessment

        fields = [
            "title",
            "assessment_type",
            "start_date",
            "end_date",
            "auto_evaluate",
            "duration",
            "extra_retakes",
            "randomize_questions",
            "question_count",
            "post_message",
        ]

        widgets = {

            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter assessment title"
            }),

            "assessment_type": forms.Select(attrs={
                "class": "form-control"
            }),

            "duration": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1
            }),

            "extra_retakes": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0
            }),

            "question_count": forms.Select(attrs={
                "class": "form-control"
            }),

            "randomize_questions": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),

            "auto_evaluate": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),

            "post_message": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Message shown after submission"
            }),
        }

        labels = {
            "title": "Assessment Title",
            "assessment_type": "Assessment Type",
            "start_date": "Start Date and Time",
            "end_date": "End Date and Time",
            "duration": "Quiz Duration (minutes)",
            "extra_retakes": "Number of Extra Retakes",
            "question_count": "Number of Questions",
            "randomize_questions": "Randomize Questions",
            "auto_evaluate": "Automatically Evaluate",
            "post_message": "Post Assessment Message",
        }

    # --------------------------------------
    # VALIDATE ASSESSMENT
    # --------------------------------------

    def clean(self):

        cleaned_data = super().clean()

        start = cleaned_data.get("start_date")
        end = cleaned_data.get("end_date")

        duration = cleaned_data.get("duration")
        extra_retakes = cleaned_data.get("extra_retakes")
        question_count = cleaned_data.get("question_count")

        if start and end and end <= start:
            self.add_error(
                "end_date",
                "The end date must be after the start date."
            )

        if duration is not None and duration < 1:
            self.add_error(
                "duration",
                "Duration must be at least one minute."
            )

        if extra_retakes is not None and extra_retakes < 0:
            self.add_error(
                "extra_retakes",
                "Extra retakes cannot be negative."
            )

        if question_count not in [10, 50]:
            self.add_error(
                "question_count",
                "Choose either 10 or 50 questions."
            )

        return cleaned_data


# ==========================================
# 2. QUESTION CREATION FORM
# ==========================================

class QuestionForm(forms.ModelForm):

    options_text = forms.CharField(
        required=False,

        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 5,
            "placeholder": (
                "For MCQ, enter one option per line.\n"
                "For Matching, enter pairs like:\n"
                "HTML = Structure\n"
                "CSS = Styling"
            )
        }),

        label="Options / Matching Pairs",

        help_text=(
            "Enter one option per line for MCQ. "
            "For Matching, use Left = Right."
        )
    )

    class Meta:
        model = Question

        fields = [
            "question_text",
            "question_type",
            "correct_answer",
            "marks",
        ]

        widgets = {

            "question_text": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Enter your question here..."
            }),

            "question_type": forms.Select(attrs={
                "class": "form-control",
                "id": "questionType"
            }),

            "correct_answer": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Enter the correct answer or evaluation guidance"
            }),

            "marks": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1
            }),
        }

        labels = {
            "question_text": "Question",
            "question_type": "Question Type",
            "correct_answer": "Correct Answer / Evaluation Guidance",
            "marks": "Marks",
        }

    # --------------------------------------
    # VALIDATE QUESTION
    # --------------------------------------

    def clean(self):

        cleaned_data = super().clean()

        question_type = cleaned_data.get("question_type")

        options_text = cleaned_data.get(
            "options_text", ""
        ).strip()

        correct_answer = cleaned_data.get(
            "correct_answer", ""
        ).strip()

        marks = cleaned_data.get("marks")

        # Split options into lines
        options = [
            line.strip()
            for line in options_text.splitlines()
            if line.strip()
        ]

        # Validate marks
        if marks is not None and marks < 1:

            self.add_error(
                "marks",
                "Marks must be at least 1."
            )

        # ==================================
        # MULTIPLE CHOICE QUESTIONS
        # ==================================

        if question_type == "mcq":

            if len(options) < 2:

                self.add_error(
                    "options_text",
                    "Enter at least two answer options."
                )

            # Remove duplicate options
            unique_options = []
            seen_options = set()

            for option in options:

                normalized = option.casefold()

                if normalized not in seen_options:

                    unique_options.append(option)
                    seen_options.add(normalized)

            options = unique_options

            if len(options) < 2:

                self.add_error(
                    "options_text",
                    "Enter at least two unique options."
                )

            if not correct_answer:

                self.add_error(
                    "correct_answer",
                    "Enter the correct answer."
                )

            elif not any(
                correct_answer.casefold() == option.casefold()
                for option in options
            ):

                self.add_error(
                    "correct_answer",
                    "The correct answer must match one of your options."
                )

        # ==================================
        # TRUE / FALSE QUESTIONS
        # ==================================

        elif question_type == "true_false":

            if correct_answer.casefold() not in ["true", "false"]:

                self.add_error(
                    "correct_answer",
                    "Enter either True or False."
                )

            else:

                cleaned_data["correct_answer"] = (
                    "True"
                    if correct_answer.casefold() == "true"
                    else "False"
                )

            options = ["True", "False"]

        # ==================================
        # SHORT ANSWER QUESTIONS
        # ==================================

        elif question_type == "short":

            if not correct_answer:

                self.add_error(
                    "correct_answer",
                    "Enter the expected answer."
                )

            options = []

        # ==================================
        # FILL IN THE BLANKS
        # ==================================

        elif question_type == "fill":

            if not correct_answer:

                self.add_error(
                    "correct_answer",
                    "Enter the missing word or expected answer."
                )

            options = []

        # ==================================
        # MATCH THE FOLLOWING
        # ==================================

        elif question_type == "matching":

            pairs = []

            for line in options:

                if "=" not in line:

                    self.add_error(
                        "options_text",
                        "Use this format: HTML = Structure"
                    )

                    continue

                left, right = line.split("=", 1)

                left = left.strip()
                right = right.strip()

                if not left or not right:

                    self.add_error(
                        "options_text",
                        "Both sides of every matching pair are required."
                    )

                    continue

                pairs.append({
                    "left": left,
                    "right": right
                })

            if len(pairs) < 2:

                self.add_error(
                    "options_text",
                    "Enter at least two matching pairs."
                )

            cleaned_data["parsed_pairs"] = pairs

            options = pairs

        # ==================================
        # DESCRIPTIVE QUESTIONS
        # ==================================

        elif question_type == "long":

            if not correct_answer:

                self.add_error(
                    "correct_answer",
                    "Enter evaluation guidance for the teacher."
                )

            options = []

        # ==================================
        # CODING CHALLENGES
        # ==================================

        elif question_type == "coding":

            if not correct_answer:

                self.add_error(
                    "correct_answer",
                    "Enter the expected solution or evaluation guidance."
                )

            options = []

        cleaned_data["options"] = options

        return cleaned_data

    # --------------------------------------
    # SAVE QUESTION
    # --------------------------------------

    def save(self, commit=True):

        question = super().save(commit=False)

        question_type = self.cleaned_data["question_type"]

        question.options = self.cleaned_data.get(
            "options", []
        )

        if commit:
            question.save()

        return question
