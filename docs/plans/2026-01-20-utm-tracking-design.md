# UTM Tracking Implementation

**Date:** 2026-01-20
**Status:** Implemented

## Overview

Simple UTM tracking to measure which marketing channels bring the most registrations.

## How It Works

1. **User visits with UTM params**: `https://quietpage.app?utm_source=reddit&utm_campaign=launch-week-1`
2. **Frontend captures params**: On app load, UTM params are stored in localStorage
3. **User registers**: UTM data is sent along with registration form
4. **Backend stores**: UTM fields saved on User model

## Marketing Links Format

```
https://quietpage.app?utm_source=reddit&utm_medium=social&utm_campaign=launch-week-1
https://quietpage.app?utm_source=hackernews&utm_medium=social&utm_campaign=launch-week-1
https://quietpage.app?utm_source=twitter&utm_medium=social&utm_campaign=launch-week-1
https://quietpage.app?utm_source=linkedin&utm_medium=social&utm_campaign=launch-week-1
https://quietpage.app?utm_source=indiehackers&utm_medium=referral&utm_campaign=launch-week-1
```

## Database Fields

On `User` model:
- `utm_source` - Traffic source (reddit, twitter, hackernews)
- `utm_medium` - Marketing medium (social, referral, email)
- `utm_campaign` - Campaign name (launch-week-1)
- `referrer` - Full referrer URL when user first visited

## Querying Data

```python
# Count registrations by source
User.objects.exclude(utm_source='').values('utm_source').annotate(count=Count('id'))

# Filter by campaign
User.objects.filter(utm_campaign='launch-week-1')

# See all users from Reddit
User.objects.filter(utm_source='reddit')
```

## Files Changed

- `apps/accounts/models.py` - Added UTM fields to User model
- `apps/api/auth_serializers.py` - Accept UTM fields in registration
- `frontend/src/hooks/useUtmTracking.ts` - New hook for capturing/storing UTM params
- `frontend/src/pages/SignupPage.tsx` - Include UTM data in registration
- `frontend/src/main.tsx` - Capture UTM params on app load
