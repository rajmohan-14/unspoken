from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Post, Reply, SessionKarma


def feed(request):
    """
    Homepage. Shows all approved, non-expired posts.
    Supports filtering by mood and category via query params.
    e.g. /?mood=anxious&category=career
    """
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

    context = {
        'posts':    posts,
        'mood':     mood,
        'category': category,
        'moods':    Post.MOOD_CHOICES,
        'categories': Post.CATEGORY_CHOICES,
    }
    return render(request, 'confessions/feed.html', context)


def submit_post(request):
    """
    GET  → show the submission form
    POST → validate and save the new post
    """
    if request.method == 'POST':
        content  = request.POST.get('content', '').strip()
        mood_tag = request.POST.get('mood_tag', '')
        category = request.POST.get('category', '')

        errors = []
        if not content:
            errors.append('Post cannot be empty.')
        if len(content) > 500:
            errors.append('Post must be under 500 characters.')
        if not mood_tag:
            errors.append('Please select a mood.')
        if not category:
            errors.append('Please select a category.')

        if not errors:
            Post.objects.create(
                session_token=request.session_token,
                content=content,
                mood_tag=mood_tag,
                category=category,
                is_approved=False,  # goes to moderation queue first
            )
            return redirect('feed')

        context = {
            'errors':     errors,
            'moods':      Post.MOOD_CHOICES,
            'categories': Post.CATEGORY_CHOICES,
        }
        return render(request, 'confessions/submit.html', context)

    context = {
        'moods':      Post.MOOD_CHOICES,
        'categories': Post.CATEGORY_CHOICES,
    }
    return render(request, 'confessions/submit.html', context)


def post_detail(request, post_id):
    """
    Shows a single post with all its replies.
    Also handles new reply submissions.
    """
    post    = get_object_or_404(Post, id=post_id, is_approved=True)
    replies = post.replies.filter(is_flagged=False).order_by('created_at')

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content and len(content) <= 300:
            Reply.objects.create(
                post=post,
                session_token=request.session_token,
                content=content,
            )
            return redirect('post_detail', post_id=post.id)

    context = {
        'post':    post,
        'replies': replies,
    }
    return render(request, 'confessions/post_detail.html', context)
