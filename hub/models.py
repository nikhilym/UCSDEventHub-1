from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
import pytz

# Create your models here.
class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null = True)
    location = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    image = models.ImageField(upload_to="events")
    hashtags = models.CharField(max_length=255)
    organizer = models.CharField(max_length=255)
    contact_email = models.EmailField()
    # create_user = models.CharField(max_length = 255, validators=[MinLengthValidator(1)])
    # create_date = models.DateTimeField(null = False)
    # modify_user = models.CharField(max_length = 255, validators=[MinLengthValidator(1)])
    # modify_date = models.DateTimeField(null = False)
    # delete_date = models.DateTimeField(null = True)

class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete = models.CASCADE, primary_key=True)
    user_is_organization = models.BooleanField(default = False)
    user_image = models.ImageField(
        upload_to="users", default=None, null = True, blank = True)

class OrganizationDetails(models.Model):
    organization = models.OneToOneField(
        User, on_delete = models.CASCADE, primary_key=True)
    description = models.TextField(null = True, blank=True)
    contact_first_name = models.CharField(max_length = 255, null = False)
    contact_last_name = models.CharField(max_length = 255, null = False)
    contact_email = models.EmailField(null = False)
    address = models.TextField(null = True, blank=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: "\
                + "'+999999999'. Up to 15 digits allowed.")
    # Using E.164 as recommended phone number format
    contact_number = models.CharField(
        validators = [phone_regex], max_length = 15, blank = True, null=True)