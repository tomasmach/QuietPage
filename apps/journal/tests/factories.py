"""
Factory Boy factories for journal app tests.

These factories create test Entry instances with encrypted content.
"""

import factory
from factory.django import DjangoModelFactory
from faker import Faker
from apps.journal.models import Entry
from apps.accounts.tests.factories import UserFactory

fake = Faker(['cs_CZ'])


class EntryFactory(DjangoModelFactory):
    """
    Factory for creating Entry instances with realistic Czech content.
    
    The content is automatically encrypted when saved to the database.
    
    Usage:
        entry = EntryFactory(user=user)
        entry = EntryFactory(title='My Day', content='Today was great!')
        entry = EntryFactory(created_at=some_datetime)  # Override auto_now_add
        entries = EntryFactory.create_batch(5, user=user)
    """
    
    class Meta:
        model = Entry
        skip_postgeneration_save = True  # Prevent extra save after post_generation
    
    user = factory.SubFactory(UserFactory)
    title = factory.Faker('sentence', nb_words=4, locale='cs_CZ')
    content = factory.Faker('paragraph', nb_sentences=5, locale='cs_CZ')
    mood_rating = factory.Faker('random_int', min=1, max=5)
    
    # word_count is calculated automatically in model.save()
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """
        Override _create to handle created_at parameter properly.
        
        Django's auto_now_add=True prevents setting created_at during creation.
        This override allows tests to set created_at by updating after creation.
        """
        from django.db.models import signals
        
        # Extract created_at if provided
        created_at_override = kwargs.pop('created_at', None)
        
        # If created_at override is provided, temporarily disable post_save signal
        # to prevent it from firing with the wrong timestamp
        if created_at_override is not None:
            from apps.journal.signals import update_streak_on_entry_create
            signals.post_save.disconnect(update_streak_on_entry_create, sender=model_class)
        
        try:
            # Create the instance normally
            instance = super()._create(model_class, *args, **kwargs)
            
            # If created_at was provided, update it using queryset
            # (bypasses auto_now_add restriction)
            if created_at_override is not None:
                model_class.objects.filter(pk=instance.pk).update(created_at=created_at_override)
                instance.refresh_from_db()
                # Manually trigger signal with correct created_at
                update_streak_on_entry_create(model_class, instance, created=True)
        finally:
            # Re-enable signal if it was disabled
            if created_at_override is not None:
                from apps.journal.signals import update_streak_on_entry_create
                signals.post_save.connect(update_streak_on_entry_create, sender=model_class)
        
        return instance
    
    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        """
        Add tags to the entry after creation.
        
        Usage:
            EntryFactory(tags=['work', 'personal'])
        """
        if not create:
            return
        
        if extracted:
            for tag in extracted:
                self.tags.add(tag)


class EntryWithoutMoodFactory(EntryFactory):
    """
    Factory for entries without mood rating.
    
    Usage:
        entry = EntryWithoutMoodFactory(user=user)
    """
    mood_rating = None


class ShortEntryFactory(EntryFactory):
    """
    Factory for short entries (< 100 words).
    
    Usage:
        entry = ShortEntryFactory(user=user)
    """
    content = factory.Faker('sentence', nb_words=20, locale='cs_CZ')


class LongEntryFactory(EntryFactory):
    """
    Factory for long entries (> 500 words).
    
    Usage:
        entry = LongEntryFactory(user=user)
    """
    content = factory.Faker('text', max_nb_chars=3000, locale='cs_CZ')
