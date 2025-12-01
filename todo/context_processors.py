from django.conf import settings


def version(request):
    return {"APP_VERSION": settings.VERSION}
