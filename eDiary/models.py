from django.db import models
from django.contrib.auth.models import User


class Signup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    mobileNumber = models.CharField(max_length=15, null=True)
    profileImage = models.ImageField(upload_to='profiles/', null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    onboarding_done = models.BooleanField(default=False)
    regDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.first_name if self.user else str(self.id)


class Category(models.Model):
    signup = models.ForeignKey(Signup, on_delete=models.CASCADE, null=True)
    categoryName = models.CharField(max_length=150, null=True)
    CreationDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.categoryName or ''


class Notes(models.Model):
    signup = models.ForeignKey(Signup, on_delete=models.CASCADE, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    noteTitle = models.CharField(max_length=150, null=True)
    noteDescription = models.CharField(max_length=250, null=True)
    CreationDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.noteTitle or ''


class Noteshistory(models.Model):
    note = models.ForeignKey(Notes, on_delete=models.CASCADE, null=True)
    signup = models.ForeignKey(Signup, on_delete=models.CASCADE, null=True)
    noteDetails = models.CharField(max_length=250, null=True)
    postingDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.noteDetails or ''
