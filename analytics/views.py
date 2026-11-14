from django.shortcuts import render


def home(request):
    return render(request, "home.html")


def module_page(request, module):
    modules = {
        "learning": {
            "icon": "📚",
            "title": "Learning",
            "subtitle": "Courses & Lessons",
            "description": "Explore courses, lessons and continue your learning journey.",
        },

        "languages": {
            "icon": "🌍",
            "title": "Language AI",
            "subtitle": "Learn in your language",
            "description": "Learn and understand educational content in multiple languages.",
        },

        "videos": {
            "icon": "🎥",
            "title": "Video AI",
            "subtitle": "Captions & Transcription",
            "description": "Watch learning videos and work with captions and transcripts.",
        },

        "summary": {
            "icon": "🧠",
            "title": "Summary AI",
            "subtitle": "Smart Summaries",
            "description": "Turn long lessons and learning material into simple summaries.",
        },

        "notes": {
            "icon": "📝",
            "title": "Notes AI",
            "subtitle": "Automatic Notes",
            "description": "Create structured and easy-to-review learning notes.",
        },

        "tutor": {
            "icon": "🤖",
            "title": "Tutor AI",
            "subtitle": "Your Personal AI Teacher",
            "description": "Ask questions and learn with your personal AI learning assistant.",
        },

        "adaptive": {
            "icon": "🎯",
            "title": "Adaptive AI",
            "subtitle": "Personalized Learning",
            "description": "Follow a learning path based on your progress and goals.",
        },

        "quizzes": {
            "icon": "🧪",
            "title": "Quiz AI",
            "subtitle": "Automatic Question Generation",
            "description": "Practice your knowledge with interactive quizzes.",
        },

        "analytics": {
            "icon": "📊",
            "title": "Analytics AI",
            "subtitle": "Performance Analysis",
            "description": "Understand your learning progress, scores and areas for improvement.",
        },

        "gamification": {
            "icon": "🎮",
            "title": "Gamification",
            "subtitle": "XP, Badges & Levels",
            "description": "Earn XP, unlock badges and build your learning streak.",
        },

        "voice": {
            "icon": "🎤",
            "title": "Voice AI",
            "subtitle": "Voice Learning",
            "description": "Use your voice to interact with your learning assistant.",
        },

        "learntwin": {
            "icon": "🧠",
            "title": "LearnTwin",
            "subtitle": "Personal Learning Intelligence",
            "description": "Build your personal learning profile and understand your strengths.",
        },

        "community": {
            "icon": "👥",
            "title": "Community",
            "subtitle": "Study Together",
            "description": "Connect with other learners and participate in study groups.",
        },

        "offline": {
            "icon": "📱",
            "title": "Offline Learning",
            "subtitle": "Learn Anywhere",
            "description": "Access selected learning content even when you are offline.",
        },

        "career": {
            "icon": "💼",
            "title": "Career AI",
            "subtitle": "Skills & Career Recommendations",
            "description": "Explore skills and career paths based on your learning journey.",
        },

        "portfolio": {
            "icon": "🏆",
            "title": "Portfolio",
            "subtitle": "Certificates & Skills",
            "description": "Showcase your completed courses, certificates and skills.",
        },
    }

    selected_module = modules.get(module)

    if selected_module is None:
        return render(request, "module.html", {
            "module": {
                "icon": "❓",
                "title": "Module Not Found",
                "subtitle": "Unknown Module",
                "description": "The requested module does not exist.",
            }
        })

    return render(request, "module.html", {
        "module": selected_module
    })