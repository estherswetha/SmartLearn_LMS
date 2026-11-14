from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from openai import OpenAI


@require_POST
def generate_transcript(request):

    video_file = request.FILES.get("video")

    if not video_file:
        return JsonResponse({
            "success": False,
            "error": "Please upload a video."
        })

    if video_file.size > 25 * 1024 * 1024:
        return JsonResponse({
            "success": False,
            "error": "Video is larger than 25 MB. Please upload a smaller video."
        })

    try:

        client = OpenAI()

        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=video_file,
            response_format="verbose_json",
            timestamp_granularities=["segment"]
        )

        segments = []

        for segment in transcription.segments:

            segments.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text
            })

        return JsonResponse({
            "success": True,
            "text": transcription.text,
            "segments": segments
        })

    except Exception as error:

        print("Video AI error:", error)

        return JsonResponse({
            "success": False,
            "error": "Unable to generate transcript."
        })


# Create your views here.