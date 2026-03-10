from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import JsonResponse
from .models import Post, Reply, SessionKindness, ModerationQueue
from .filters import should_auto_approve, check_flagged, check_crisis
from moderator.utils import check_and_nominate 
from django.db import models

def feed(request):
    import json
    import os
    from django.conf import settings

    posts = Post.objects.filter(
        is_approved=True,
        expires_at__gt=timezone.now()
    ).order_by('-created_at')

    mood     = request.GET.get('mood', '')
    category = request.GET.get('category', '')

    if mood:
        posts = posts.filter(mood_tag=mood)
    if category:
        posts = posts.filter(category=category)


    highlights      = []
    highlights_path = os.path.join(settings.BASE_DIR, 'weekly_highlights.json')
    if os.path.exists(highlights_path):
        try:
            with open(highlights_path, 'r') as f:
                data       = json.load(f)
                highlights = data.get('highlights', [])
        except (json.JSONDecodeError, KeyError):
            highlights = []

    # Board stats for widget
    from .models import Reply, SessionKindness
    stats = {
        'total_posts':   Post.objects.filter(is_approved=True).count(),
        'total_replies': Reply.objects.count(),
        'total_kindness': SessionKindness.objects.aggregate(
            total=models.Sum('kindness_points')
        )['total'] or 0,
    }

    context = {
        'posts':      posts,
        'mood':       mood,
        'category':   category,
        'moods':      Post.MOOD_CHOICES,
        'categories': Post.CATEGORY_CHOICES,
        'highlights': highlights,
        'stats':      stats,
    }
    return render(request, 'confessions/feed.html', context)

def submit_post(request):
    crisis   = False
    errors   = []

    if request.method == 'POST':
        content  = request.POST.get('content', '').strip()
        mood_tag = request.POST.get('mood_tag', '')
        category = request.POST.get('category', '')

        # Check for crisis keywords
        crisis = check_crisis(content)

        if not content:
            errors.append('Post cannot be empty.')
        elif len(content) > 500:
            errors.append('Post must be under 500 characters.')
        if not mood_tag:
            errors.append('Please select a mood.')
        if not category:
            errors.append('Please select a category.')

        if not errors:
          
            auto_approve = should_auto_approve(content)
            is_flagged   = check_flagged(content)

            post = Post.objects.create(
                session_token = request.session_token,
                content       = content,
                mood_tag      = mood_tag,
                category      = category,
                is_approved   = auto_approve,
            )

            # Send flagged posts to moderation queue
            if is_flagged:
                ModerationQueue.objects.create(
                    post   = post,
                    reason = 'Auto-flagged by keyword filter',
                )

            if auto_approve:
                return redirect('feed')
            else:
                return redirect('post_pending')

    context = {
        'errors':     errors,
        'crisis':     crisis,
        'moods':      Post.MOOD_CHOICES,
        'categories': Post.CATEGORY_CHOICES,
    }
    return render(request, 'confessions/submit.html', context)


def post_pending(request):
    
    return render(request, 'confessions/post_pending.html')


def post_detail(request, post_id):
    post    = get_object_or_404(Post, id=post_id, is_approved=True)
    replies = post.replies.filter(is_flagged=False).order_by('created_at')

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content and len(content) <= 300:
            Reply.objects.create(
                post          = post,
                session_token = request.session_token,
                content       = content,
            )
            return redirect('post_detail', post_id=post.id)

    context = {
        'post':    post,
        'replies': replies,
    }
    return render(request, 'confessions/post_detail.html', context)


def vote_helpful(request, reply_id):
   
    if request.method == 'POST':
        reply = get_object_or_404(Reply, id=reply_id)

       
        if reply.session_token == request.session_token:
            return JsonResponse({'error': 'Cannot vote on your own reply'}, status=400)

       
        reply.helpful_votes += 1
        reply.save()

        kindness, created = SessionKindness.objects.get_or_create(
            session_token=reply.session_token,
            defaults={'kindness_points': 0, 'people_helped': 0}
        )
        kindness.kindness_points += 1
        kindness.people_helped += 1
        kindness.save()
        from moderator.utils import check_and_nominate
        check_and_nominate(reply.session_token)
    
        reply.post.kindness_received += 1
        reply.post.save()

        return JsonResponse({
            'helpful_votes': reply.helpful_votes,
            'message': 'Vote recorded'
        })

    return JsonResponse({'error': 'POST required'}, status=405)


def report_post(request, post_id):
    """User-reported content goes to moderation queue."""
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        
        if not ModerationQueue.objects.filter(post=post, status='pending').exists():
            ModerationQueue.objects.create(
                post   = post,
                reason = 'User reported',
            )
        return JsonResponse({'message': 'Reported. Thank you.'})
    return JsonResponse({'error': 'POST required'}, status=405)