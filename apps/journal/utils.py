"""
Utility functions for journal app.

Includes streak calculation, timezone handling, and inspirational quotes.
"""

from datetime import timedelta
import logging
import pytz
import random
from django.utils import timezone

logger = logging.getLogger(__name__)


def get_user_local_date(utc_datetime, user_timezone):
    """
    Convert UTC datetime to user's local date.
    Handles DST transitions and invalid timezones gracefully.

    Args:
        utc_datetime: Timezone-aware datetime in UTC
        user_timezone: User's timezone string (e.g., 'Europe/Prague')

    Returns:
        date object in user's local timezone (falls back to UTC on error)
    """
    try:
        tz = pytz.timezone(str(user_timezone))
    except pytz.UnknownTimeZoneError:
        logger.error(f"Invalid timezone: {user_timezone}, using UTC fallback")
        tz = pytz.UTC

    # astimezone() handles DST transitions automatically
    local_dt = utc_datetime.astimezone(tz)
    return local_dt.date()


def update_user_streak(user, entry_created_at):
    """
    Update user's writing streak when new entry is created.

    Logic:
    - First entry ever: streak = 1
    - Same day entry: no change (multiple entries per day don't extend streak)
    - Backdated entry: ignore (entry_date < last_entry_date, preserves current streak)
    - Consecutive day: increment streak (entry_date = last_entry_date + 1)
    - Gap detected: reset to 1 (entry_date > last_entry_date + 1)

    Backdated entries are ignored to allow users to journal about past events
    without breaking their current streak. Only future-dated entries that create
    gaps will reset the streak.

    Uses atomic transaction with row-level locking to prevent race conditions
    when multiple entries are created concurrently.

    Args:
        user: User instance
        entry_created_at: DateTime when entry was created (UTC, timezone-aware)

    Note:
        All comparisons use date-only values in the user's local timezone to
        avoid timezone-related edge cases (e.g., 11:59pm vs 12:01am).
    """
    from django.db import transaction
    from apps.accounts.models import User

    # Convert to user's local date (ensures date-only comparison)
    entry_date = get_user_local_date(entry_created_at, user.timezone)

    # Atomic transaction with row lock to prevent concurrent update issues
    with transaction.atomic():
        # Refresh user from database with exclusive lock
        user = User.objects.select_for_update().get(pk=user.pk)

        if user.last_entry_date is None:
            # First entry ever
            user.current_streak = 1
            user.longest_streak = 1
            user.last_entry_date = entry_date
        elif entry_date == user.last_entry_date:
            # Same day - multiple entries don't extend streak
            return  # No update needed
        elif entry_date < user.last_entry_date:
            # Backdated entry - ignore for streak computation
            # User is adding old entries, don't break their current streak
            return  # No update needed
        elif entry_date == user.last_entry_date + timedelta(days=1):
            # Consecutive day - increment streak
            user.current_streak += 1
            # Update longest if we broke the record
            if user.current_streak > user.longest_streak:
                user.longest_streak = user.current_streak
            user.last_entry_date = entry_date
        else:
            # Gap detected (entry_date > last_entry_date + 1 day) - streak broken
            user.current_streak = 1
            user.last_entry_date = entry_date

        user.save(update_fields=['current_streak', 'longest_streak', 'last_entry_date'])


def recalculate_user_streak(user):
    """
    Recalculate streak from scratch based on entry history.
    
    Useful for:
    - Data verification
    - Fixing corrupted streak data
    - Admin tools
    
    Returns:
        dict with current_streak and longest_streak
    """
    from .models import Entry
    
    # Only include entries with actual content (word_count > 0)
    # This matches the signal logic for streak updates
    entries = Entry.objects.filter(user=user, word_count__gt=0).order_by('created_at')
    
    if not entries.exists():
        return {'current_streak': 0, 'longest_streak': 0}
    
    # Get all unique dates (in user's timezone)
    dates = sorted(set(
        get_user_local_date(entry.created_at, user.timezone)
        for entry in entries
    ))
    
    # Calculate current streak (working backwards from today)
    today = get_user_local_date(timezone.now(), user.timezone)
    current_streak = 0
    
    for i in range(len(dates) - 1, -1, -1):
        expected_date = today - timedelta(days=current_streak)
        if dates[i] == expected_date:
            current_streak += 1
        else:
            break
    
    # Calculate longest streak (scan through all dates)
    longest_streak = 1
    temp_streak = 1
    
    for i in range(1, len(dates)):
        if dates[i] - dates[i-1] == timedelta(days=1):
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            temp_streak = 1
    
    return {
        'current_streak': current_streak,
        'longest_streak': longest_streak
    }


# Inspirational quotes for empty state
INSPIRATIONAL_QUOTES = [
    {
        'text': 'Psaní je cesta k poznání sama sebe.',
        'author': None
    },
    {
        'text': 'Každý záznam je krok k jasnější mysli.',
        'author': None
    },
    {
        'text': 'Tvé myšlenky si zaslouží být vyslyšeny.',
        'author': None
    },
    {
        'text': 'Journaling není o dokonalosti, je o upřímnosti.',
        'author': None
    },
    {
        'text': 'Začni odtud, začni teď.',
        'author': None
    },
    {
        'text': 'Píšeš pro sebe, ne pro ostatní.',
        'author': None
    },
    {
        'text': 'Klid přichází, když myšlenky najdou místo na papíře.',
        'author': None
    },
    {
        'text': 'Každý den je nová stránka.',
        'author': None
    },
]


def get_random_quote():
    """
    Get a random inspirational quote for empty state.

    Returns:
        dict with 'text' and 'author' (author can be None)
    """
    return random.choice(INSPIRATIONAL_QUOTES)


def get_today_date_range(user):
    """
    Get start and end datetime for today in user's timezone.
    Handles invalid timezones gracefully with UTC fallback.

    Returns tuple of (today_start, today_end) as timezone-aware datetimes.
    """
    try:
        user_tz = pytz.timezone(str(user.timezone))
    except pytz.UnknownTimeZoneError:
        logger.error(f"Invalid timezone: {user.timezone}, using UTC fallback")
        user_tz = pytz.UTC

    now = timezone.now().astimezone(user_tz)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    return today_start, today_end


def parse_tags(tags_data):
    """
    Parse tags from string or list format.

    Args:
        tags_data: Either a comma-separated string or a list of tags

    Returns:
        List of tag strings, or None if tags_data is None
    """
    if tags_data is None:
        return None

    if isinstance(tags_data, str):
        return [tag.strip() for tag in tags_data.split(',') if tag.strip()]
    elif isinstance(tags_data, list):
        return [str(tag).strip() for tag in tags_data if str(tag).strip()]

    return []


# ============================================
# DATA EXPORT UTILITIES
# ============================================


def upload_export_to_secure_storage(user_id, user_data):
    """
    Upload user data export to secure storage.

    Creates a JSON file with the user's exported data and saves it to
    Django's default storage backend. Files are stored in a private
    'exports' directory with a UUID-based filename.

    Args:
        user_id (int): ID of the user whose data is being exported
        user_data (dict): Complete user data export dictionary

    Returns:
        str: Storage path to the uploaded file

    Raises:
        Exception: If file upload fails

    Note:
        - Files persist indefinitely in storage. The 48-hour time limit applies
          only to the download token (created in send_export_link_email), not the
          file itself. A cleanup task should be implemented to remove expired
          exports from storage.
        - Ensure default_storage is configured as private in production (e.g.,
          S3 bucket with restricted ACLs) to prevent unauthorized access to
          exported files.
    """
    import json
    import uuid
    from django.core.files.base import ContentFile
    from django.core.files.storage import default_storage

    # Generate secure filename with UUID (unguessable, cryptographically random)
    # Format: user_{id}_{uuid}.json for ownership validation + unpredictability
    unique_id = uuid.uuid4()
    filename = f'exports/user_{user_id}_{unique_id}.json'

    # Convert data to JSON
    json_content = json.dumps(user_data, indent=2, ensure_ascii=False)
    json_bytes = json_content.encode('utf-8')

    # Upload to storage
    storage_path = default_storage.save(filename, ContentFile(json_bytes))

    logger.info(f"User data export saved to storage: {storage_path}")
    return storage_path


def send_export_link_email(user_email, username, storage_path):
    """
    Send email with time-limited, signed download link for user data export.

    Generates a cryptographically signed token that expires after 48 hours
    and queues an async Celery task to send the download link via email.

    Args:
        user_email (str): User's email address
        username (str): User's username (for personalization)
        storage_path (str): Storage path to the export file (used to derive filename)

    Returns:
        bool: True if email task was queued successfully

    Security:
        - Uses Django's TimestampSigner for cryptographic signatures
        - Tokens expire after 48 hours
        - Download endpoint validates signature and user ownership
    """
    from django.conf import settings
    from django.core.signing import TimestampSigner
    from apps.accounts.tasks import send_email_async
    from urllib.parse import urlencode

    # Extract filename from storage path
    filename = storage_path.split('/')[-1]

    # Create signed token with 48-hour expiration
    # Token format: "filename:signature:timestamp"
    # Salt must match ExportDownloadView validation to ensure token verification works
    signer = TimestampSigner(salt='export-download')
    signed_token = signer.sign(filename)

    # Generate secure download URL with signed token (properly URL-encoded)
    base_url = str(settings.SITE_URL).rstrip('/')
    download_url = f"{base_url}/api/exports/download/?{urlencode({'token': signed_token})}"

    # Email content
    subject = 'QuietPage - Your Data Export is Ready'
    plain_message = f"""Ahoj {username},

Tvůj export dat je připravený ke stažení.

Odkaz ke stažení:
{download_url}

Tento odkaz vyprší za 48 hodin z bezpečnostních důvodů.

Export obsahuje:
- Tvůj profil a nastavení
- Všechny záznamy z deníku (dešifrované)
- Statistiky a tagy

Pokud jsi o tento export nežádal/a, ihned nás kontaktuj.

QuietPage tým
{settings.SITE_URL}
"""

    try:
        # Queue async email task
        send_email_async.delay(
            subject=subject,
            plain_message=plain_message,
            recipient_list=[user_email]
        )
        logger.info("Export download link email queued")
        return True
    except Exception as e:
        logger.error(f"Failed to queue export email: {e}", exc_info=True)
        return False
