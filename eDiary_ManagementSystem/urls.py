from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from eDiary import views

handler404 = 'eDiary.views.custom_404'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('privacy', views.privacy_policy, name='privacy'),
    path('terms', views.terms_of_service, name='terms'),
    path('registration', views.registration, name='registration'),
    path('user_login', views.user_login, name='user_login'),
    path('verify/<uidb64>/<token>/', views.verify_email, name='verify_email'),
    path('resend-verification', views.resend_verification, name='resend_verification'),
    path('password-reset', views.password_reset_request, name='password_reset'),
    path('password-reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password-reset/done/', views.password_reset_complete, name='password_reset_complete'),
    path('user_home', views.user_home, name='user_home'),
    path('onboarding/complete', views.complete_onboarding, name='complete_onboarding'),
    path('manageCategory', views.manageCategory, name='manageCategory'),
    path('editCategory/<int:pid>', views.editCategory, name='editCategory'),
    path('deleteCategory/<int:pid>', views.deleteCategory, name='deleteCategory'),
    path('manageNotes', views.manageNotes, name='manageNotes'),
    path('editNotes/<int:pid>', views.editNotes, name='editNotes'),
    path('viewNotes/<int:pid>', views.viewNotes, name='viewNotes'),
    path('deleteNotesHistory/<int:pid>', views.deleteNotesHistory, name='deleteNotesHistory'),
    path('deleteNotes/<int:pid>', views.deleteNotes, name='deleteNotes'),
    path('searchNotes', views.searchNotes, name='searchNotes'),
    path('profile', views.profile, name='profile'),
    path('changePassword', views.changePassword, name='changePassword'),
    path('delete-account', views.delete_account, name='delete_account'),
    path('logout/', views.Logout, name='logout'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
