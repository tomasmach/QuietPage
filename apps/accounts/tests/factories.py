"""
Factory Boy factories for accounts app tests.

These factories provide convenient ways to create test data with realistic
values, reducing boilerplate in test files.
"""

import factory
from factory.django import DjangoModelFactory
from faker import Faker
from django.contrib.auth import get_user_model
from apps.accounts.models import EmailChangeRequest
from django.utils import timezone
from datetime import timedelta

fake = Faker(['cs_CZ'])  # Czech locale for realistic data
User = get_user_model()


class UserFactory(DjangoModelFactory):
    """
    Factory for creating User instances with realistic Czech data.
    
    Usage:
        user = UserFactory()  # Creates user with random data
        user = UserFactory(username='johndoe')  # Override specific fields
        users = UserFactory.create_batch(10)  # Create multiple users
    """
    
    class Meta:
        model = User
        django_get_or_create = ('username',)
    
    # Basic auth fields
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    
    # Profile fields
    # first_name = factory.Faker('first_name', locale='cs_CZ')
    # last_name = factory.Faker('last_name', locale='cs_CZ')
    bio = factory.Faker('text', max_nb_chars=200, locale='cs_CZ')
    
    # Settings
    timezone = 'Europe/Prague'
    email_notifications = False
    daily_word_goal = 750
    preferred_writing_time = 'morning'
    reminder_enabled = False
    reminder_time = factory.Faker('time_object')
    
    # Streak tracking
    current_streak = 0
    longest_streak = 0
    last_entry_date = None
    
    # Timestamps
    is_active = True
    is_staff = False
    is_superuser = False


class AdminUserFactory(UserFactory):
    """
    Factory for creating admin/superuser instances.
    
    Usage:
        admin = AdminUserFactory()
    """
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'admin{n}')
    is_staff = True
    is_superuser = True


class EmailChangeRequestFactory(DjangoModelFactory):
    """
    Factory for creating EmailChangeRequest instances.
    
    Usage:
        request = EmailChangeRequestFactory(user=user)
        request = EmailChangeRequestFactory(user=user, created_at=some_datetime)
    """
    
    class Meta:
        model = EmailChangeRequest
    
    user = factory.SubFactory(UserFactory)
    new_email = factory.Faker('email')
    is_verified = False
    
    # expires_at is set automatically in model.save()
    # but we can override it for testing
    @factory.lazy_attribute
    def expires_at(self):
        return timezone.now() + timedelta(hours=24)
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """
        Override _create to handle created_at parameter properly.
        
        Django's auto_now_add=True prevents setting created_at during creation.
        This override allows tests to set created_at by updating after creation.
        """
        # Extract created_at if provided
        created_at_override = kwargs.pop('created_at', None)
        
        # Create the instance normally
        instance = super()._create(model_class, *args, **kwargs)
        
        # If created_at was provided, update it using queryset
        # (bypasses auto_now_add restriction)
        if created_at_override is not None:
            model_class.objects.filter(pk=instance.pk).update(created_at=created_at_override)
            instance.refresh_from_db()
        
        return instance


class ExpiredEmailChangeRequestFactory(EmailChangeRequestFactory):
    """
    Factory for creating expired EmailChangeRequest instances.
    
    Usage:
        expired_request = ExpiredEmailChangeRequestFactory(user=user)
    """
    
    @factory.lazy_attribute
    def expires_at(self):
        return timezone.now() - timedelta(hours=1)  # Expired 1 hour ago
    
    @factory.lazy_attribute
    def created_at(self):
        return timezone.now() - timedelta(hours=25)  # Created 25 hours ago
