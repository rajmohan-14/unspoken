from django.urls import path
from . import views

urlpatterns = [
    path('',                          views.feed,        name='feed'),
    path('submit/',                   views.submit_post, name='submit_post'),
    path('post/<int:post_id>/',       views.post_detail, name='post_detail'),
    path('post/pending/',             views.post_pending, name='post_pending'),
    path('vote/<int:reply_id>/',      views.vote_helpful, name='vote_helpful'),
    path('report/<int:post_id>/',     views.report_post,  name='report_post'),
]