from celery import shared_task
from django.utils import timezone


@shared_task
def delete_expired_posts():
   
    from .models import Post

    expired = Post.objects.filter(expires_at__lt=timezone.now())
    count   = expired.count()
    expired.delete()

    return f"Deleted {count} expired posts"


@shared_task
def highlight_weekly_kindness():
   
    from .models import SessionKindness
    import json
    import os
    from django.conf import settings

    current_week = timezone.now().isocalendar()[1]

    top_helpers = SessionKindness.objects.filter(
        week_number=current_week
    ).order_by('-kindness_points')[:3]

    highlights = [
        {
            'rank':             i + 1,
            'kindness_points':  helper.kindness_points,
            'people_helped':    helper.people_helped,
        }
        for i, helper in enumerate(top_helpers)
    ]

    highlights_path = os.path.join(settings.BASE_DIR, 'weekly_highlights.json')
    with open(highlights_path, 'w') as f:
        import json
        json.dump({
            'week':       current_week,
            'highlights': highlights,
            'generated':  timezone.now().isoformat(),
        }, f)

    return f"Weekly highlights saved for week {current_week}"


@shared_task
def update_kindness_week_numbers():
  
    from .models import SessionKindness

    current_week = timezone.now().isocalendar()[1]
    updated      = SessionKindness.objects.exclude(
        week_number=current_week
    ).update(week_number=current_week)

    return f"Updated {updated} kindness records to week {current_week}"