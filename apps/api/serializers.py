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
    timezone = serializers.SerializerMethodField()

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
            'preferred_language',
            'preferred_theme',
            'onboarding_completed',
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

    def get_timezone(self, obj):
        """Return timezone as string instead of ZoneInfo object."""
        return str(obj.timezone) if obj.timezone else 'Europe/Prague'


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
    today_words = serializers.IntegerField()
    daily_goal = serializers.IntegerField()
    total_entries = serializers.IntegerField()
    current_streak = serializers.IntegerField()
    longest_streak = serializers.IntegerField()
    total_words = serializers.IntegerField()


class StatisticsSerializer(serializers.Serializer):
    """
    Serializer for statistics API response.

    Defines the structure for aggregated journal analytics.
    """
    period = serializers.CharField()
    mood_analytics = serializers.DictField()
    word_count_analytics = serializers.DictField()
    writing_patterns = serializers.DictField()
    tag_analytics = serializers.DictField()

    def validate_period(self, value):
        """
        Validate that period is one of the allowed values.

        Args:
            value: The period string to validate.

        Returns:
            str: The validated period.

        Raises:
            ValidationError: If period is not one of the allowed values.
        """
        valid_periods = ['7d', '30d', '90d', '1y', 'all']
        if value not in valid_periods:
            raise serializers.ValidationError(
                f"Period must be one of: {', '.join(valid_periods)}"
            )
        return value
