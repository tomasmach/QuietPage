"""
Serializers for QuietPage API.

This module defines serializers for User, Entry, and dashboard statistics.
"""

from rest_framework import serializers
from apps.accounts.models import User
from apps.journal.models import Entry


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.

    Includes profile information, writing goals, streak data, and preferences.
    """
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'avatar',
            'bio',
            'timezone',
            'daily_word_goal',
            'current_streak',
            'longest_streak',
            'email_notifications',
            'preferred_writing_time',
            'reminder_enabled',
            'reminder_time',
        ]
        read_only_fields = ['id', 'current_streak', 'longest_streak']

    def get_avatar(self, obj):
        """Return full URL for avatar if it exists."""
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None


class EntryListSerializer(serializers.ModelSerializer):
    """
    Serializer for Entry list view (without content for performance).

    Used for dashboard and list views where full content is not needed.
    """
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Entry
        fields = [
            'id',
            'title',
            'mood_rating',
            'word_count',
            'tags',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'word_count', 'created_at', 'updated_at']

    def get_tags(self, obj):
        """Return tags as list of strings."""
        return [tag.name for tag in obj.tags.all()]


class EntrySerializer(serializers.ModelSerializer):
    """
    Full serializer for Entry model with content.

    Used for detail view, create, and update operations.
    """
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Entry
        fields = [
            'id',
            'title',
            'content',
            'mood_rating',
            'word_count',
            'tags',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'word_count', 'created_at', 'updated_at']

    def get_tags(self, obj):
        """Return tags as list of strings."""
        return [tag.name for tag in obj.tags.all()]

    def create(self, validated_data):
        """
        Create a new entry and associate it with the authenticated user.

        Tags are handled separately since they're a ManyToMany field.
        """
        tags_data = self.initial_data.get('tags', [])

        # Create entry with user from context
        entry = Entry.objects.create(
            user=self.context['request'].user,
            **validated_data
        )

        # Set tags if provided
        if tags_data:
            entry.tags.set(*tags_data)

        return entry

    def update(self, instance, validated_data):
        """
        Update an existing entry.

        Tags are handled separately since they're a ManyToMany field.
        """
        tags_data = self.initial_data.get('tags', None)

        # Update regular fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update tags if provided in request
        if tags_data is not None:
            instance.tags.set(*tags_data)

        return instance


class DashboardStatsSerializer(serializers.Serializer):
    """
    Serializer for dashboard statistics.

    This is not a ModelSerializer as it aggregates data from multiple sources.
    """
    total_entries = serializers.IntegerField()
    current_streak = serializers.IntegerField()
    longest_streak = serializers.IntegerField()
    total_words = serializers.IntegerField()
