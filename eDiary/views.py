from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponseNotFound
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.http import require_POST

from .models import Category, Notes, Noteshistory, Signup
from .utils import (
    email_verify_token,
    get_user_signup,
    owned_category,
    owned_history,
    owned_note,
    rate_limit,
    require_signup,
    uid_for_user,
    validate_email,
    validate_mobile,
    validate_password,
)


def index(request):
    return render(request, 'index.html')


def privacy_policy(request):
    return render(request, 'privacy.html')


def terms_of_service(request):
    return render(request, 'terms.html')


def custom_404(request, exception=None):
    return render(request, '404.html', status=404)


@rate_limit('register', limit=5, window=120, template='registration.html')
def registration(request):
    error = ""
    error_message = ""
    if request.method == "POST":
        firstName = (request.POST.get('firstName') or '').strip()
        lastName = (request.POST.get('lastName') or '').strip()
        emailid = (request.POST.get('emailid') or '').strip().lower()
        Password = request.POST.get('Password') or ''
        mobileNumber = (request.POST.get('mobileNumber') or '').strip()

        if not firstName or not lastName:
            error, error_message = "yes", "Please enter your first and last name."
        elif not validate_email(emailid):
            error, error_message = "yes", "Please enter a valid email address."
        elif User.objects.filter(username=emailid).exists():
            error, error_message = "yes", "An account with this email already exists."
        elif not validate_mobile(mobileNumber):
            error, error_message = "yes", "Mobile number must be exactly 10 digits."
        else:
            ok, msg = validate_password(Password)
            if not ok:
                error, error_message = "yes", msg
            else:
                try:
                    user = User.objects.create_user(
                        username=emailid,
                        email=emailid,
                        password=Password,
                        first_name=firstName,
                        last_name=lastName,
                        is_active=True,
                    )
                    Signup.objects.create(
                        user=user,
                        mobileNumber=mobileNumber,
                        email_verified=False,
                        onboarding_done=False,
                    )
                    _send_verification_email(request, user)
                    error = "no"
                except Exception:
                    error, error_message = "yes", "Could not create account. Please try again."
    return render(request, 'registration.html', locals())


def _send_verification_email(request, user):
    uid = uid_for_user(user)
    token = email_verify_token.make_token(user)
    link = request.build_absolute_uri(
        reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
    )
    subject = 'Verify your eDiary email'
    message = (
        f'Hi {user.first_name},\n\n'
        f'Please verify your email for eDiary by opening this link:\n{link}\n\n'
        f'If you did not sign up, ignore this message.\n'
    )
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email or user.username], fail_silently=True)
    except Exception:
        pass


def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None
    if user and email_verify_token.check_token(user, token):
        signup = get_user_signup(user)
        if signup:
            signup.email_verified = True
            signup.save()
        return render(request, 'verify_email_done.html', {'ok': True})
    return render(request, 'verify_email_done.html', {'ok': False})


@require_signup
@rate_limit('resend_verify', limit=3, window=300, redirect_to='user_home')
@require_POST
def resend_verification(request):
    _send_verification_email(request, request.user)
    return redirect(reverse('user_home') + '?verify=sent')


@rate_limit('login', limit=8, window=60, template='user_login.html')
def user_login(request):
    error = ""
    error_message = ""
    if request.user.is_authenticated:
        return redirect('user_home')
    if request.method == 'POST':
        e = (request.POST.get('emailid') or '').strip().lower()
        p = request.POST.get('password') or ''
        if not e or not p:
            error, error_message = "yes", "Email and password are required."
        else:
            user = authenticate(username=e, password=p)
            if user is not None:
                login(request, user)
                error = "no"
            else:
                error, error_message = "yes", "Invalid email or password."
    return render(request, 'user_login.html', locals())


@require_signup
def user_home(request):
    signup = request.signup
    totalcategory = Category.objects.filter(signup=signup).count()
    totalnotes = Notes.objects.filter(signup=signup).count()
    notes = Notes.objects.filter(signup=signup).order_by('-id')[:20]
    show_onboarding = (not signup.onboarding_done) and totalcategory == 0 and totalnotes == 0
    verify_sent = request.GET.get('verify') == 'sent'
    return render(request, 'user_home.html', locals())


@require_signup
@require_POST
def complete_onboarding(request):
    signup = request.signup
    signup.onboarding_done = True
    signup.save()
    return redirect('manageCategory')


@require_signup
def manageCategory(request):
    signup = request.signup
    category = Category.objects.filter(signup=signup)
    error = ""
    error_message = ""
    if request.method == "POST":
        categoryName = (request.POST.get('categoryName') or '').strip()
        if not categoryName:
            error, error_message = "yes", "Category name is required."
        elif len(categoryName) > 150:
            error, error_message = "yes", "Category name is too long."
        else:
            try:
                Category.objects.create(signup=signup, categoryName=categoryName)
                if not signup.onboarding_done:
                    signup.onboarding_done = True
                    signup.save()
                error = "no"
            except Exception:
                error, error_message = "yes", "Could not save category."
    return render(request, 'manageCategory.html', locals())


@require_signup
def editCategory(request, pid):
    signup = request.signup
    category = owned_category(signup, pid)
    error = ""
    error_message = ""
    if request.method == "POST":
        categoryName = (request.POST.get('categoryName') or '').strip()
        if not categoryName:
            error, error_message = "yes", "Category name is required."
        else:
            category.categoryName = categoryName
            try:
                category.save()
                error = "no"
            except Exception:
                error, error_message = "yes", "Could not update category."
    return render(request, 'editCategory.html', locals())


@require_signup
def deleteCategory(request, pid):
    category = owned_category(request.signup, pid)
    category.delete()
    return redirect('manageCategory')


@require_signup
def manageNotes(request):
    signup = request.signup
    category = Category.objects.filter(signup=signup)
    notes = Notes.objects.filter(signup=signup)
    error = ""
    error_message = ""
    if request.method == "POST":
        cid = request.POST.get('category')
        noteTitle = (request.POST.get('noteTitle') or '').strip()
        noteDescription = (request.POST.get('noteDescription') or '').strip()
        if not cid:
            error, error_message = "yes", "Please select a category."
        elif not noteTitle:
            error, error_message = "yes", "Note title is required."
        elif not noteDescription:
            error, error_message = "yes", "Note description is required."
        else:
            try:
                categoryid = owned_category(signup, cid)
                Notes.objects.create(
                    signup=signup,
                    category=categoryid,
                    noteTitle=noteTitle,
                    noteDescription=noteDescription,
                )
                error = "no"
            except Exception:
                error, error_message = "yes", "Could not save note."
    return render(request, 'manageNotes.html', locals())


@require_signup
def editNotes(request, pid):
    signup = request.signup
    notes = owned_note(signup, pid)
    category = Category.objects.filter(signup=signup)
    error = ""
    error_message = ""
    if request.method == "POST":
        cid = request.POST.get('category')
        noteTitle = (request.POST.get('noteTitle') or '').strip()
        noteDescription = (request.POST.get('noteDescription') or '').strip()
        if not cid or not noteTitle or not noteDescription:
            error, error_message = "yes", "All fields are required."
        else:
            try:
                categoryid = owned_category(signup, cid)
                notes.category = categoryid
                notes.noteTitle = noteTitle
                notes.noteDescription = noteDescription
                notes.save()
                error = "no"
            except Exception:
                error, error_message = "yes", "Could not update note."
    return render(request, 'editNotes.html', locals())


@require_signup
def viewNotes(request, pid):
    signup = request.signup
    notes = owned_note(signup, pid)
    noteshistory = Noteshistory.objects.filter(signup=signup, note=notes)
    error = ""
    error_message = ""
    if request.method == "POST":
        noteDetails = (request.POST.get('noteDetails') or '').strip()
        if not noteDetails:
            error, error_message = "yes", "Please enter note details."
        else:
            try:
                Noteshistory.objects.create(note=notes, signup=signup, noteDetails=noteDetails)
                error = "no"
            except Exception:
                error, error_message = "yes", "Could not add note details."
    return render(request, 'viewNotes.html', locals())


@require_signup
def deleteNotesHistory(request, pid):
    noteshistory = owned_history(request.signup, pid)
    note_id = noteshistory.note_id
    noteshistory.delete()
    if note_id:
        return redirect('viewNotes', pid=note_id)
    return redirect('manageNotes')


@require_signup
def deleteNotes(request, pid):
    notes = owned_note(request.signup, pid)
    notes.delete()
    return redirect('manageNotes')


@require_signup
def searchNotes(request):
    signup = request.signup
    notes = []
    sd = ''
    searched = False
    if request.method == 'POST':
        sd = (request.POST.get('search') or '').strip()
        searched = True
        if sd:
            notes = Notes.objects.filter(signup=signup, noteTitle__icontains=sd)
    return render(request, 'searchNotes.html', locals())


@require_signup
def profile(request):
    signup = request.signup
    error = ""
    error_message = ""
    if request.method == "POST":
        fname = (request.POST.get('firstName') or '').strip()
        lname = (request.POST.get('lastName') or '').strip()
        mob = (request.POST.get('mobileNumber') or '').strip()
        if not fname or not lname:
            error, error_message = "yes", "Name fields are required."
        elif mob and not validate_mobile(mob):
            error, error_message = "yes", "Mobile number must be exactly 10 digits."
        else:
            signup.user.first_name = fname
            signup.user.last_name = lname
            signup.mobileNumber = mob
            if request.FILES.get('profileImage'):
                signup.profileImage = request.FILES['profileImage']
            try:
                signup.save()
                signup.user.save()
                error = "no"
            except Exception:
                error, error_message = "yes", "Could not update profile."
    return render(request, 'profile.html', locals())


@require_signup
def changePassword(request):
    error = ""
    error_message = ""
    if request.method == "POST":
        o = request.POST.get('oldpassword') or ''
        n = request.POST.get('newpassword') or ''
        c = request.POST.get('confirmpassword') or ''
        ok, msg = validate_password(n)
        if n != c:
            error, error_message = "yes", "New password and confirm password do not match."
        elif not ok:
            error, error_message = "yes", msg
        elif not request.user.check_password(o):
            error, error_message = "not", "Your current password is wrong."
        else:
            try:
                request.user.set_password(n)
                request.user.save()
                error = "no"
            except Exception:
                error, error_message = "yes", "Could not update password."
    return render(request, 'changePassword.html', locals())


@require_signup
def delete_account(request):
    if request.method == 'POST':
        confirm = (request.POST.get('confirm') or '').strip().upper()
        password = request.POST.get('password') or ''
        if confirm != 'DELETE':
            return render(request, 'delete_account.html', {
                'error': 'yes',
                'error_message': 'Type DELETE to confirm account deletion.',
            })
        if not request.user.check_password(password):
            return render(request, 'delete_account.html', {
                'error': 'yes',
                'error_message': 'Password is incorrect.',
            })
        user = request.user
        signup = request.signup
        logout(request)
        Noteshistory.objects.filter(signup=signup).delete()
        Notes.objects.filter(signup=signup).delete()
        Category.objects.filter(signup=signup).delete()
        signup.delete()
        user.delete()
        return redirect('index')
    return render(request, 'delete_account.html')


def Logout(request):
    logout(request)
    return redirect('index')


# ---- Password reset (custom thin wrappers around Django auth tokens) ----

@rate_limit('pwd_reset', limit=5, window=300, template='password_reset.html')
def password_reset_request(request):
    error = ""
    error_message = ""
    if request.method == 'POST':
        email = (request.POST.get('email') or '').strip().lower()
        if not validate_email(email):
            error, error_message = "yes", "Enter a valid email address."
        else:
            user = User.objects.filter(username=email).first() or User.objects.filter(email=email).first()
            # Always show success to avoid email enumeration
            if user:
                uid = uid_for_user(user)
                token = default_token_generator.make_token(user)
                link = request.build_absolute_uri(
                    reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                )
                send_mail(
                    'Reset your eDiary password',
                    f'Hi {user.first_name},\n\nReset your password here:\n{link}\n\nIf you did not ask for this, ignore the email.\n',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email or user.username],
                    fail_silently=True,
                )
            error = "no"
    return render(request, 'password_reset.html', locals())


def password_reset_confirm(request, uidb64, token):
    error = ""
    error_message = ""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None
    valid = bool(user and default_token_generator.check_token(user, token))
    if not valid:
        return render(request, 'password_reset_confirm.html', {'valid': False})
    if request.method == 'POST':
        n = request.POST.get('password') or ''
        c = request.POST.get('confirm') or ''
        ok, msg = validate_password(n)
        if n != c:
            error, error_message = "yes", "Passwords do not match."
        elif not ok:
            error, error_message = "yes", msg
        else:
            user.set_password(n)
            user.save()
            return redirect('password_reset_complete')
    return render(request, 'password_reset_confirm.html', {
        'valid': True,
        'error': error,
        'error_message': error_message,
        'uidb64': uidb64,
        'token': token,
    })


def password_reset_complete(request):
    return render(request, 'password_reset_complete.html')
