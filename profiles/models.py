from django.db import models
from django.conf import settings
from django.utils import timezone


class Profile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Man'),
        ('W', 'Woman'),
        ('NB', 'Non-binary'),
        ('O', 'Other'),
    ]
    INTEREST_CHOICES = [
        ('M', 'Men'),
        ('W', 'Women'),
        ('E', 'Everyone'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=5, choices=GENDER_CHOICES, blank=True)
    interested_in = models.CharField(max_length=5, choices=INTEREST_CHOICES, default='E')
    location = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    education = models.CharField(max_length=100, blank=True)
    is_verified = models.BooleanField(default=False)
    is_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'profiles'

    def __str__(self):
        return f"{self.first_name} ({self.user.email})"

    @property
    def age(self):
        if self.birth_date:
            today = timezone.now().date()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None

    @property
    def primary_photo(self):
        photo = self.photos.filter(is_primary=True).first()
        if not photo:
            photo = self.photos.first()
        return photo


class ProfilePhoto(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='profile_pics/%Y/%m/')
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'profile_photos'
        ordering = ['order', 'uploaded_at']

    def __str__(self):
        return f"Photo for {self.profile.first_name}"


class Interest(models.Model):
    name = models.CharField(max_length=50, unique=True)
    emoji = models.CharField(max_length=10, blank=True)

    class Meta:
        db_table = 'interests'

    def __str__(self):
        return self.name


class ProfileInterest(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='profile_interests')
    interest = models.ForeignKey(Interest, on_delete=models.CASCADE)

    class Meta:
        db_table = 'profile_interests'
        unique_together = ['profile', 'interest']
