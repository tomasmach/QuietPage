"""
Django management command for seeding realistic journal entry data.

This command creates realistic journal entries for testing statistics features.
Entries are distributed across a date range with realistic patterns, word counts,
moods, tags, and writing times.

Usage:
    python manage.py seed_entries
    python manage.py seed_entries --username=tomik --days=90 --coverage=75 --clear

Interactive mode (default):
    Prompts for username, days, coverage percentage, and clear option

Arguments:
    --username: Username of the user to seed entries for
    --days: Number of days to seed (backwards from today)
    --coverage: Percentage of days that will have entries (0-100)
    --clear: Clear existing entries before seeding (asks for confirmation)
    --no-input: Skip all prompts (use with all other args)
"""

import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from faker import Faker

from apps.journal.models import Entry

User = get_user_model()
fake = Faker(["cs_CZ"])

# Predefined Czech tags for realistic data
CZECH_TAGS = [
    "práce",
    "rodina",
    "cestování",
    "zdraví",
    "sport",
    "hobby",
    "přátelé",
    "vztahy",
    "vzdělávání",
    "finance",
    "domov",
    "nákupy",
    "vaření",
    "čítání",
    "filmy",
    "hudba",
    "příroda",
    "víkend",
    "oslavy",
    "plány",
]


class Command(BaseCommand):
    help = "Seed realistic journal entries for testing statistics"

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--username",
            type=str,
            help="Username of the user to seed entries for",
        )
        parser.add_argument(
            "--days",
            type=int,
            help="Number of days to seed (backwards from today)",
        )
        parser.add_argument(
            "--coverage",
            type=int,
            help="Percentage of days that will have entries (0-100)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing entries in the date range before seeding",
        )
        parser.add_argument(
            "--no-input",
            action="store_true",
            help="Skip all prompts (requires all other arguments)",
        )

    def _prompt_username(self):
        """Prompt for username and validate it exists."""
        while True:
            username = input("Enter username: ").strip()
            if not username:
                self.stdout.write(self.style.ERROR("Username cannot be empty"))
                continue

            try:
                user = User.objects.get(username=username)
                return user
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User "{username}" does not exist'))
                retry = input("Try again? (y/n): ").strip().lower()
                if retry != "y":
                    raise CommandError("User not found. Aborting.")

    def _prompt_days(self):
        """Prompt for number of days to seed."""
        while True:
            days_input = input(
                "Enter number of days to seed (e.g., 90, 180, 365) [90]: "
            ).strip()
            if not days_input:
                return 90  # Default

            try:
                days = int(days_input)
                if days <= 0:
                    self.stdout.write(self.style.ERROR("Days must be positive"))
                    continue
                if days > 3650:  # 10 years max
                    self.stdout.write(
                        self.style.ERROR("Days cannot exceed 3650 (10 years)")
                    )
                    continue
                return days
            except ValueError:
                self.stdout.write(self.style.ERROR("Please enter a valid number"))

    def _prompt_coverage(self):
        """Prompt for coverage percentage."""
        while True:
            coverage_input = input(
                "Enter coverage percentage (0-100, e.g., 70 = 70% of days have entries) [70]: "
            ).strip()
            if not coverage_input:
                return 70  # Default

            try:
                coverage = int(coverage_input)
                if coverage < 0 or coverage > 100:
                    self.stdout.write(
                        self.style.ERROR("Coverage must be between 0 and 100")
                    )
                    continue
                return coverage
            except ValueError:
                self.stdout.write(self.style.ERROR("Please enter a valid number"))

    def _prompt_clear(self, user, start_date, end_date):
        """Prompt whether to clear existing entries."""
        existing_count = Entry.objects.filter(
            user=user, created_at__gte=start_date, created_at__lte=end_date
        ).count()

        if existing_count == 0:
            return False

        self.stdout.write(
            self.style.WARNING(
                f"\nFound {existing_count} existing entries for {user.username} "
                f"between {start_date.date()} and {end_date.date()}"
            )
        )
        clear = (
            input("Clear existing entries before seeding? (y/n) [n]: ").strip().lower()
        )
        return clear == "y"

    def _generate_word_count(self, daily_goal):
        """
        Generate realistic word count with variance.

        Distribution:
        - 60% above goal (750-2000 words)
        - 30% below goal (300-749 words)
        - 10% very short or empty (0-299 words)
        """
        rand = random.random()

        if rand < 0.60:  # 60% above goal
            return random.randint(daily_goal, daily_goal + 1250)
        elif rand < 0.90:  # 30% below goal
            return random.randint(300, daily_goal - 1)
        else:  # 10% very short/empty
            return random.randint(0, 299)

    def _generate_content(self, word_count):
        """Generate Czech content with approximate word count."""
        if word_count == 0:
            return ""

        # Generate text and adjust to match word count
        paragraphs = []
        current_words = 0
        target_words = word_count

        while current_words < target_words:
            # Generate a paragraph with ~100-150 words
            paragraph = fake.paragraph(nb_sentences=random.randint(5, 10))
            paragraphs.append(paragraph)
            current_words += len(paragraph.split())

        content = "\n\n".join(paragraphs)
        words = content.split()

        # Trim to exact word count
        if len(words) > target_words:
            words = words[:target_words]
            content = " ".join(words)

        return content

    def _generate_mood(self):
        """
        Generate random mood rating.

        Distribution:
        - 70-80% have mood ratings (1-5)
        - 20-30% no mood rating (None)
        - Slightly skewed towards positive moods (3-5)
        """
        if random.random() < 0.25:  # 25% no mood
            return None

        # Weighted towards positive moods
        moods = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5]
        return random.choice(moods)

    def _generate_tags(self):
        """
        Generate random tags for an entry.

        Distribution:
        - 30% no tags
        - 40% 1-2 tags
        - 20% 3-4 tags
        - 10% 5+ tags
        """
        rand = random.random()

        if rand < 0.30:  # 30% no tags
            return []
        elif rand < 0.70:  # 40% 1-2 tags
            num_tags = random.randint(1, 2)
        elif rand < 0.90:  # 20% 3-4 tags
            num_tags = random.randint(3, 4)
        else:  # 10% 5+ tags
            num_tags = random.randint(5, 7)

        return random.sample(CZECH_TAGS, min(num_tags, len(CZECH_TAGS)))

    def _generate_time_of_day(self, preferred_time):
        """
        Generate realistic time of day based on user preference.

        Time clusters around preferred_writing_time with some variance.
        """
        # Map preferred time to hour ranges
        time_ranges = {
            "morning": (6, 12),  # 6 AM - 12 PM
            "afternoon": (12, 18),  # 12 PM - 6 PM
            "evening": (18, 23),  # 6 PM - 11 PM
            "anytime": (6, 23),  # 6 AM - 11 PM
        }

        hour_range = time_ranges.get(preferred_time, (6, 23))

        # 70% within preferred range, 30% outside
        if random.random() < 0.70:
            hour = random.randint(hour_range[0], hour_range[1])
        else:
            # Random hour outside preferred range
            all_hours = list(range(0, 24))
            preferred_hours = list(range(hour_range[0], hour_range[1] + 1))
            other_hours = [h for h in all_hours if h not in preferred_hours]
            hour = random.choice(other_hours) if other_hours else random.randint(0, 23)

        minute = random.randint(0, 59)
        second = random.randint(0, 59)

        return hour, minute, second

    def _select_days_to_seed(self, total_days, coverage_percentage):
        """
        Select which days will have entries based on coverage percentage.

        Creates realistic patterns with occasional streaks and gaps.
        """
        num_days_with_entries = int(total_days * coverage_percentage / 100)

        # Start with random selection
        days_with_entries = set(random.sample(range(total_days), num_days_with_entries))

        # Add some realistic streaks (3-7 consecutive days)
        num_streaks = max(
            1, num_days_with_entries // 20
        )  # ~5% of entry days start a streak

        for _ in range(num_streaks):
            if len(days_with_entries) >= num_days_with_entries:
                break

            # Pick a random day and extend it into a streak
            streak_start = random.randint(0, total_days - 1)
            streak_length = random.randint(3, 7)

            for i in range(streak_length):
                day = streak_start + i
                if day < total_days and len(days_with_entries) < num_days_with_entries:
                    days_with_entries.add(day)

        # Ensure we have exactly the right number of days
        days_list = sorted(list(days_with_entries))
        if len(days_list) > num_days_with_entries:
            days_list = days_list[:num_days_with_entries]

        return set(days_list)

    def _create_entry(self, user, date, user_tz):
        """Create a single entry with realistic data."""
        # Generate realistic data
        word_count_target = self._generate_word_count(user.daily_word_goal)
        content = self._generate_content(word_count_target)
        mood = self._generate_mood()
        tags = self._generate_tags()

        # Generate time of day
        hour, minute, second = self._generate_time_of_day(user.preferred_writing_time)

        # Create datetime in user's timezone
        entry_datetime = date.replace(hour=hour, minute=minute, second=second)

        # Generate title (30% of entries have titles)
        title = ""
        if random.random() < 0.30:
            title = fake.sentence(nb_words=random.randint(3, 6))[:-1]  # Remove period

        # Create entry
        # Skip validation to allow manual created_at
        entry = Entry(
            user=user,
            title=title,
            content=content,
            mood_rating=mood,
        )

        # Save without validation to bypass created_at auto_now_add
        entry.save(skip_validation=True)

        # Update created_at using queryset (bypasses auto_now_add)
        Entry.objects.filter(pk=entry.pk).update(created_at=entry_datetime)
        entry.refresh_from_db()

        # Add tags
        if tags:
            entry.tags.add(*tags)

        # Note: Don't manually trigger streak update signal here
        # Streak will be recalculated at the end for accuracy

        return entry

    def handle(self, *args, **options):
        """Execute the seed command."""
        no_input = options["no_input"]

        # Get or prompt for username
        if options["username"]:
            try:
                user = User.objects.get(username=options["username"])
            except User.DoesNotExist:
                raise CommandError(f'User "{options["username"]}" does not exist')
        else:
            if no_input:
                raise CommandError("--username is required when using --no-input")
            user = self._prompt_username()

        # Get or prompt for days
        if options["days"] is not None:
            days = options["days"]
            if days <= 0:
                raise CommandError("Days must be positive")
            if days > 3650:
                raise CommandError("Days cannot exceed 3650 (10 years)")
        else:
            if no_input:
                raise CommandError("--days is required when using --no-input")
            days = self._prompt_days()

        # Get or prompt for coverage
        if options["coverage"] is not None:
            coverage = options["coverage"]
            if coverage < 0 or coverage > 100:
                raise CommandError("Coverage must be between 0 and 100")
        else:
            if no_input:
                raise CommandError("--coverage is required when using --no-input")
            coverage = self._prompt_coverage()

        # Calculate date range in user's timezone
        user_tz = ZoneInfo(str(user.timezone))
        now = timezone.now().astimezone(user_tz)
        end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        start_date = (now - timedelta(days=days - 1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        # Get or prompt for clear option
        should_clear = options["clear"]
        if not no_input and not should_clear:
            should_clear = self._prompt_clear(user, start_date, end_date)

        # Display summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("SEED ENTRIES SUMMARY"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"User:           {user.username}")
        self.stdout.write(f"Timezone:       {user.timezone}")
        self.stdout.write(f"Daily Goal:     {user.daily_word_goal} words")
        self.stdout.write(
            f"Date Range:     {start_date.date()} to {end_date.date()} ({days} days)"
        )
        self.stdout.write(
            f"Coverage:       {coverage}% ({int(days * coverage / 100)} days with entries)"
        )
        self.stdout.write(f"Clear Existing: {'Yes' if should_clear else 'No'}")
        self.stdout.write("=" * 60 + "\n")

        # Confirm before proceeding
        if not no_input:
            confirm = input("Proceed with seeding? (y/n) [y]: ").strip().lower()
            if confirm and confirm != "y":
                self.stdout.write(self.style.WARNING("Aborted by user"))
                return

        # Execute seeding in transaction
        try:
            with transaction.atomic():
                # Clear existing entries if requested
                if should_clear:
                    deleted_count = Entry.objects.filter(
                        user=user, created_at__gte=start_date, created_at__lte=end_date
                    ).delete()[0]
                    self.stdout.write(
                        self.style.WARNING(
                            f"✓ Deleted {deleted_count} existing entries"
                        )
                    )

                # Select days to seed
                days_to_seed = self._select_days_to_seed(days, coverage)

                # Create entries
                created_entries = []
                self.stdout.write("\nSeeding entries...")

                for day_offset in sorted(days_to_seed):
                    # Calculate date for this entry
                    entry_date = start_date + timedelta(days=day_offset)

                    # Create entry
                    entry = self._create_entry(user, entry_date, user_tz)
                    created_entries.append(entry)

                    # Progress indicator
                    if len(created_entries) % 10 == 0:
                        self.stdout.write(
                            f"  Created {len(created_entries)} entries...", ending="\r"
                        )

                self.stdout.write("")  # New line after progress

                # Recalculate user streak from scratch (more accurate than incremental updates)
                from apps.journal.utils import recalculate_user_streak

                streak_data = recalculate_user_streak(user)
                user.current_streak = streak_data["current_streak"]
                user.longest_streak = streak_data["longest_streak"]
                # Set last_entry_date to the most recent entry with content
                last_entry = (
                    Entry.objects.filter(user=user, word_count__gt=0)
                    .order_by("-created_at")
                    .first()
                )
                if last_entry:
                    from apps.journal.utils import get_user_local_date

                    user.last_entry_date = get_user_local_date(
                        last_entry.created_at, user.timezone
                    )
                user.save(
                    update_fields=[
                        "current_streak",
                        "longest_streak",
                        "last_entry_date",
                    ]
                )

                # Calculate statistics
                total_words = sum(e.word_count for e in created_entries)
                avg_words = total_words / len(created_entries) if created_entries else 0
                entries_with_mood = sum(
                    1 for e in created_entries if e.mood_rating is not None
                )
                entries_meeting_goal = sum(
                    1 for e in created_entries if e.word_count >= user.daily_word_goal
                )

                # Refresh user to get final streak values
                user.refresh_from_db()

                # Display results
                self.stdout.write("\n" + "=" * 60)
                self.stdout.write(self.style.SUCCESS("SEEDING COMPLETE"))
                self.stdout.write("=" * 60)
                self.stdout.write(f"Entries Created:      {len(created_entries)}")
                self.stdout.write(f"Total Words:          {total_words:,}")
                self.stdout.write(f"Average Words/Entry:  {avg_words:.0f}")
                self.stdout.write(
                    f"Entries with Mood:    {entries_with_mood} ({entries_with_mood / len(created_entries) * 100:.0f}%)"
                )
                self.stdout.write(
                    f"Entries Meeting Goal: {entries_meeting_goal} ({entries_meeting_goal / len(created_entries) * 100:.0f}%)"
                )
                self.stdout.write(f"Current Streak:       {user.current_streak} days")
                self.stdout.write(f"Longest Streak:       {user.longest_streak} days")
                self.stdout.write("=" * 60)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\n✓ Successfully seeded {len(created_entries)} entries for {user.username}"
                    )
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n✗ Error during seeding: {str(e)}"))
            raise
