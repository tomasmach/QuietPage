"""
Management command to re-encrypt entries from shared key to per-user encryption.

This command finds entries with key_version=None (encrypted with old shared key)
and re-encrypts them with each user's personal encryption key.

Usage:
    python manage.py migrate_encrypted_entries [--dry-run] [--user-id USER_ID]
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from cryptography.fernet import Fernet, InvalidToken
from apps.journal.models import Entry
from apps.accounts.models import EncryptionKey


class Command(BaseCommand):
    help = "Re-encrypt entries from shared key to per-user encryption"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without making changes',
        )
        parser.add_argument(
            '--user-id',
            type=str,
            help='Only migrate entries for specific user ID',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        user_id = options.get('user_id')

        # Get the global encryption key
        global_key = getattr(settings, 'FIELD_ENCRYPTION_KEY', None)
        if not global_key:
            raise CommandError(
                "FIELD_ENCRYPTION_KEY not found in settings. "
                "Make sure FERNET_KEY_PRIMARY environment variable is set."
            )

        if isinstance(global_key, str):
            global_key = global_key.encode('utf-8')

        global_fernet = Fernet(global_key)
        master_fernet = Fernet(global_key)  # For decrypting user keys

        # Build query
        query = Entry.objects.select_related('user').filter(key_version__isnull=True)
        if user_id:
            query = query.filter(user_id=user_id)

        total_entries = query.count()

        if total_entries == 0:
            self.stdout.write(self.style.SUCCESS("No entries need migration."))
            return

        self.stdout.write(f"Found {total_entries} entries to migrate")

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made"))
            for entry in query[:10]:  # Show first 10
                self.stdout.write(
                    f"  Would migrate: {entry.id} (user: {entry.user.username}, "
                    f"created: {entry.created_at})"
                )
            if total_entries > 10:
                self.stdout.write(f"  ... and {total_entries - 10} more")
            return

        migrated = 0
        skipped = 0
        errors = []

        for entry in query:
            if not entry.content:
                skipped += 1
                continue

            # Get user's encryption key
            try:
                user_key = EncryptionKey.objects.get(user=entry.user)
            except EncryptionKey.DoesNotExist:
                error_msg = f"No encryption key for user {entry.user_id} (entry {entry.id})"
                errors.append(error_msg)
                self.stdout.write(self.style.ERROR(f"  ERROR: {error_msg}"))
                continue

            # Try to decrypt with global key
            try:
                plaintext = global_fernet.decrypt(entry.content.encode('utf-8')).decode('utf-8')
            except InvalidToken:
                error_msg = f"Failed to decrypt entry {entry.id} (user {entry.user_id})"
                errors.append(error_msg)
                self.stdout.write(self.style.ERROR(f"  ERROR: {error_msg}"))
                continue
            except Exception as e:
                error_msg = f"Unexpected error decrypting entry {entry.id}: {e}"
                errors.append(error_msg)
                self.stdout.write(self.style.ERROR(f"  ERROR: {error_msg}"))
                continue

            # Re-encrypt with user's key
            try:
                user_raw_key = master_fernet.decrypt(user_key.key.encode('utf-8'))
                user_fernet = Fernet(user_raw_key)
                new_content = user_fernet.encrypt(plaintext.encode('utf-8')).decode('utf-8')

                entry.content = new_content
                entry.key_version = user_key.version
                entry.save(update_fields=['content', 'key_version'])
                migrated += 1

                if migrated % 100 == 0:
                    self.stdout.write(f"  Progress: {migrated}/{total_entries}")

            except Exception as e:
                error_msg = f"Failed to re-encrypt entry {entry.id}: {e}"
                errors.append(error_msg)
                self.stdout.write(self.style.ERROR(f"  ERROR: {error_msg}"))
                continue

        # Summary
        self.stdout.write(self.style.SUCCESS(f"\nMigration complete:"))
        self.stdout.write(f"  Migrated: {migrated}")
        self.stdout.write(f"  Skipped (empty): {skipped}")

        if errors:
            self.stdout.write(self.style.ERROR(f"  Errors: {len(errors)}"))
            self.stdout.write("\nError details:")
            for error in errors:
                self.stdout.write(f"  - {error}")
        else:
            self.stdout.write(self.style.SUCCESS("  No errors!"))
