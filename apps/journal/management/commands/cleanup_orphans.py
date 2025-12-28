"""
Django management command for cleaning up orphaned data.

This command should be run periodically (e.g., weekly via cron) to:
- Delete expired email change requests (7+ days old)
- Delete unused tags that aren't associated with any entries

Usage:
    python manage.py cleanup_orphans

Cron example (run every Sunday at 2 AM):
    0 2 * * 0 cd /path/to/project && python manage.py cleanup_orphans
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count
from datetime import timedelta

from apps.accounts.models import EmailChangeRequest
from taggit.models import Tag


class Command(BaseCommand):
    help = 'Cleanup expired email requests and unused tags'

    def add_arguments(self, parser):
        """Add optional command arguments."""
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Delete email requests older than this many days (default: 7)',
        )

    def handle(self, *args, **options):
        """Execute the cleanup command."""
        dry_run = options['dry_run']
        days = options['days']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No data will be deleted'))

        # Cleanup 1: Delete expired email change requests
        cutoff = timezone.now() - timedelta(days=days)
        expired_requests = EmailChangeRequest.objects.filter(
            is_verified=False,
            expires_at__lt=cutoff
        )

        count_expired = expired_requests.count()

        if dry_run:
            self.stdout.write(
                f'Would delete {count_expired} expired email change requests (older than {days} days)'
            )
        else:
            deleted_count = expired_requests.delete()[0]
            self.stdout.write(
                self.style.SUCCESS(f'✓ Deleted {deleted_count} expired email change requests')
            )

        # Cleanup 2: Delete unused tags
        unused_tags = Tag.objects.annotate(
            num_entries=Count('journal_uuidtaggeditem_items')
        ).filter(num_entries=0)

        count_unused = unused_tags.count()

        if dry_run:
            self.stdout.write(
                f'Would delete {count_unused} unused tags'
            )
        else:
            deleted_tags = unused_tags.delete()[0]
            self.stdout.write(
                self.style.SUCCESS(f'✓ Deleted {deleted_tags} unused tags')
            )

        # Summary
        self.stdout.write('')
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN COMPLETE: Would delete {count_expired} requests + {count_unused} tags'
                )
            )
        else:
            total = deleted_count + deleted_tags
            self.stdout.write(
                self.style.SUCCESS(f'✓ Cleanup complete: {total} items removed')
            )
