import zipfile

from django import forms
from .models import ScormCourse


class ScormCourseForm(forms.ModelForm):

    class Meta:
        model = ScormCourse
        fields = ["title", "description", "package"]

    def clean_package(self):
        package = self.cleaned_data["package"]

        if not package.name.lower().endswith(".zip"):
            raise forms.ValidationError(
                "Please upload a SCORM ZIP file."
            )

        if package.size > 100 * 1024 * 1024:
            raise forms.ValidationError(
                "The ZIP file must be smaller than 100 MB."
            )

        try:
            with zipfile.ZipFile(package) as archive:
                names = archive.namelist()

                if "imsmanifest.xml" not in names:
                    raise forms.ValidationError(
                        "Invalid SCORM package: imsmanifest.xml "
                        "must be in the ZIP root."
                    )

                if archive.testzip() is not None:
                    raise forms.ValidationError(
                        "The ZIP file is damaged."
                    )

        except zipfile.BadZipFile:
            raise forms.ValidationError(
                "The uploaded file is not a valid ZIP archive."
            )

        package.seek(0)
        return package