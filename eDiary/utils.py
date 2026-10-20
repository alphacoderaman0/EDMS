import re
from functools import wraps

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import Category, Notes, Noteshistory, Signup


class EmailVerifyTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.is_active}{getattr(user, 'email', '')}"


email_verify_token = EmailVerifyTokenGenerator()


def get_client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


def rate_limit(key_prefix, limit=8, window=60, template='user_login.html', redirect_to=None):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if request.method == 'POST':
                ip = get_client_ip(request)
                cache_key = f"rl:{key_prefix}:{ip}"
                hits = cache.get(cache_key, 0)
                if hits >= limit:
                    if redirect_to:
                        return redirect(redirect_to)
                    return render(request, template, {
                        'error': 'rate',
                        'error_message': 'Too many attempts. Please wait a minute and try again.',
                    })
                cache.set(cache_key, hits + 1, window)
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


def get_user_signup(user):
    return Signup.objects.filter(user=user).first()


def require_signup(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('user_login')
        signup = get_user_signup(request.user)
        if not signup:
            return redirect('user_login')
        request.signup = signup
        return view_func(request, *args, **kwargs)
    return _wrapped


def owned_category(signup, pid):
    return get_object_or_404(Category, id=pid, signup=signup)


def owned_note(signup, pid):
    return get_object_or_404(Notes, id=pid, signup=signup)


def owned_history(signup, pid):
    return get_object_or_404(Noteshistory, id=pid, signup=signup)


def validate_email(value):
    return bool(re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', value or ''))


def validate_mobile(value):
    return bool(re.match(r'^\d{10}$', value or ''))


def validate_password(value):
    if not value or len(value) < 8:
        return False, 'Password must be at least 8 characters.'
    if value.isdigit() or value.isalpha():
        return False, 'Use a mix of letters and numbers in your password.'
    return True, ''


def uid_for_user(user):
    return urlsafe_base64_encode(force_bytes(user.pk))
