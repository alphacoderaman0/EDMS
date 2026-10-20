from eDiary.models import Signup


def user_signup(request):
    """Expose current user's Signup (for avatar in layout)."""
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return {"user_signup": None}
    try:
        return {"user_signup": Signup.objects.get(user=request.user)}
    except Signup.DoesNotExist:
        return {"user_signup": None}
