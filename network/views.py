from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import *

from django.core.paginator import Paginator

from datetime import datetime
import json


MAX_ITEMS_PER_PAGE = 10


@login_required
def index(request, following=False):
    #  #Get all posts or following users posts
    if following:
        users_i_follow = [
            f.following_user_id for f in request.user.following.all()
        ]
        posts = Post.objects.filter(user__in=users_i_follow)
    else:
        posts = Post.objects.all()

    # #Prepare UI data
    post_data = list()
    for post in posts:
        # #Get like count for this post
        likes = Likes.objects.filter(post=post).count()

        # #Check if this post is already liked by me
        already_liked = Likes.objects.filter(
            post=post,
            user=request.user
        )
        react = 'Unlike' if already_liked else 'Like'

        # #Update data
        post_data.append({
            'post_id': post.id,
            'post_text': post.text,
            'posted_by': post.user,
            'posted_at': post.created_at,
            'likes_count': likes,
            'react': react
        })

    # #Django Pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(post_data, MAX_ITEMS_PER_PAGE)
    posts = paginator.get_page(page_number)

    # #UI Params
    params = {
        'posts': posts,
    }
    return render(
        request,
        "network/index.html",
        params
    )


@login_required
def user_info(request, user_id):
    # #Get user whose info is to be viewed
    target_user = User.objects.get(pk=user_id)

    # #Get followers/followings count for this user
    following_count = target_user.following.count()
    followers_count = target_user.followers.count()

    # #Get posts created by this user
    posts = Post.objects.filter(user=target_user)

    # #Prepare UI data
    post_data = list()
    for post in posts:
        # #Get like count for this post
        likes = Likes.objects.filter(post=post).count()

        # #Check if this post is already liked by me
        already_liked = Likes.objects.filter(
            post=post,
            user=request.user
        )
        react = 'Unlike' if already_liked else 'Like'

        post_data.append({
            'post_id': post.id,
            'post_text': post.text,
            'posted_at': post.created_at,
            'likes_count': likes,
            'react': react
        })

    # #Django Pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(post_data, MAX_ITEMS_PER_PAGE)
    posts = paginator.get_page(page_number)

    """
    If target user is not session user,
    find out if this session session has followed this target user,
    if no, should be allowed to follow else should be allowed to unfollow

    Also, if target user is not the session user, don't allow post edit
    """
    action = None
    allow_edit = True
    if not target_user == request.user:
        allow_edit = False
        try:
            followed = UserFollowing.objects.get(
                user_id=request.user.id, following_user_id=user_id)
            action = 'Unfollow'
        except UserFollowing.DoesNotExist:
            action = 'Follow'

    # #Build UI Params
    params = {
        'target_user': target_user,
        'following_count': following_count,
        'followers_count': followers_count,
        'posts': posts,
        'action': action,
        'allow_edit': allow_edit
    }
    return render(request, "network/user_info.html", params)


@login_required
def follow(request, user_id):

    # #Check if target user is session user
    if user_id == request.user.id:
        message = "ERROR: Cannot perform action on self"
        status = messages.ERROR
        return JsonResponse({"message": message}, status=400)
    else:
        # #Get user which is to be followed
        target_user = User.objects.get(pk=user_id)
        followers_count = target_user.followers.count()
        try:
            # Create UserFollowing entry
            response = UserFollowing.objects.create(
                user_id=request.user,
                following_user_id=target_user,
            )
            message = "Followed user successfully"
            target_user = User.objects.get(pk=user_id)
            followers_count = target_user.followers.count()
            return JsonResponse({
                "message": message,
                "followers_count": followers_count}, status=200)
        except IntegrityError:
            message = "ERROR: Already followed this user"
            status = messages.ERROR
            return JsonResponse({"message": message}, status=400)


@login_required
def unfollow(request, user_id):
    # #Check if target user is session user
    if user_id == request.user.id:
        message = "ERROR: Cannot perform action on self"
        return JsonResponse({"message": message}, status=400)
    else:
        # #Get user which is to be un-followed
        target_user = User.objects.get(pk=user_id)
        try:
            # Delete UserFollowing entry
            existing = UserFollowing.objects.get(
                user_id=request.user,
                following_user_id=target_user,
            )
            existing.delete()
            target_user = User.objects.get(pk=user_id)
            followers_count = target_user.followers.count()
            message = "Unfollowed user successfully"
            return JsonResponse({
                "message": message,
                "followers_count": followers_count}, status=200)
        except UserFollowing.DoesNotExist:
            message = "ERROR: User is not follower"
            return JsonResponse({"message": message}, status=400)


@login_required
def like(request, post_id):
    # #Get post which is to be liked
    post = Post.objects.get(pk=post_id)

    # #Check if this post is already liked by me (session-user)
    existing = Likes.objects.filter(
        post=post,
        user=request.user
    )
    if existing:
        message = "Post already liked"
        status_code = 400
        return JsonResponse({"message": message}, status=status_code)

    else:
        response = Likes.objects.create(
            post=post,
            user=request.user
        )
        message = "Successfully liked post."
        status_code = 200
        likes_count = Likes.objects.filter(post=post).count()
    return JsonResponse({
        "message": message,
        "likes_count": likes_count}, status=status_code)


@login_required
def unlike(request, post_id):
    # #Get post which is to be un-liked
    post = Post.objects.get(pk=post_id)

    # #Check if this post is already un-liked by me (session-user)
    existing = Likes.objects.filter(
        post=post,
        user=request.user
    )
    if not existing:
        message = "Post not liked before"
        status_code = 400
        return JsonResponse({"message": message}, status=status_code)
    else:
        existing.delete()
        message = "Successfully unliked post."
        status_code = 200

        likes_count = Likes.objects.filter(post=post).count()
    return JsonResponse({
        "message": message,
        "likes_count": likes_count}, status=status_code)


@login_required
def create_post(request):
    if request.method == "POST":
        # #Create post
        response = Post.objects.create(
            text=request.POST['post_text'],
            user=request.user
        )
        # #Return to home page
        message = "Successfully created a new post."
        messages.add_message(request, messages.SUCCESS, message)
        return redirect("index")
    return render(request, "network/post.html")


@login_required
def edit_post(request, post_id):
    # #Get post and check if exists or not

    try:
        post = Post.objects.get(user=request.user, pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    if request.method == "POST":
        response = json.loads(request.body)
        # #Save post
        post.text = response['post_text']
        post.save()
        return JsonResponse({"edited_post": post.text}, status=200)

    return render(request, "network/post.html", {'post': post})


@login_required
def following_posts(request):
    # #Return to home page with following flag True
    return index(request, following=True)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        dob = request.POST['dob']

        # #Ensure the date supplied is as per the format
        try:
            dob = datetime.strptime(dob, '%Y-%m-%d')
        except ValueError:
            return render(request, "network/register.html", {
                "message": "Invalid date."
            })

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password, dob=dob)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
