from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
import traceback
from .models import *
from .serializers import *

from django.core.paginator import Paginator

from datetime import datetime

MAX_ITEMS_PER_PAGE = 10


@login_required
def index(request, following=False):
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
        likes = Likes.objects.filter(post=post).count()
        already_liked = Likes.objects.filter(
            post=post,
            user=request.user
        )
        react = 'Unlike' if already_liked else 'Like'
        post_data.append({
            'post_id': post.id,
            'post_text': post.text,
            'posted_by': post.user,
            'posted_at': post.created_at,
            'likes_count': likes,
            'react': react
        })

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
    target_user = User.objects.get(pk=user_id)
    following_count = target_user.following.count()
    followers_count = target_user.followers.count()
    posts = Post.objects.filter(user=target_user)
    print(UserFollowing.objects.all())
    post_data = list()
    for post in posts:
        likes = Likes.objects.filter(post=post).count()
        post_data.append({
            'post_id': post.id,
            'post_text': post.text,
            'posted_at': post.created_at,
            'likes_count': likes
        })
    page_number = request.GET.get('page', 1)
    paginator = Paginator(post_data, MAX_ITEMS_PER_PAGE)
    posts = paginator.get_page(page_number)

    """
    If target user is not session user,
    find out if this session session has followed this target user,
    if no, should be allowed to follow else should be allowed to unfollow
    """
    action = None
    if not target_user == request.user:
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
        'action': action
    }
    return render(request, "network/user_info.html", params)


@login_required
def follow(request, user_id):
    if user_id == request.user.id:
        message = "ERROR: Cannot perform action on self"
        status = messages.ERROR
    else:
        target_user = User.objects.get(pk=user_id)
        try:
            # Create UserFollowing entry
            response = UserFollowing.objects.create(
                user_id=request.user,
                following_user_id=target_user,
            )
            message = "Followed user successfully"
            status = messages.SUCCESS
        except IntegrityError:
            message = "ERROR: Already followed this user"
            status = messages.ERROR
    messages.add_message(request, status, message)
    return redirect("user_info", user_id=user_id)


@login_required
def unfollow(request, user_id):
    if user_id == request.user.id:
        message = "ERROR: Cannot perform action on self"
        status = messages.ERROR
    else:
        target_user = User.objects.get(pk=user_id)
        try:
            # Delete UserFollowing entry
            existing = UserFollowing.objects.get(
                user_id=request.user,
                following_user_id=target_user,
            )
            existing.delete()
            message = "Un-followed user successfully"
            status = messages.SUCCESS
        except UserFollowing.DoesNotExist:
            message = "ERROR: User is not follower"
            status = messages.ERROR
    messages.add_message(request, status, message)
    return redirect("user_info", user_id=user_id)


@login_required
def like(request, post_id):
    post = Post.objects.get(pk=post_id)
    existing = Likes.objects.filter(
        post=post,
        user=request.user
    )
    if existing:
        message = "Post already liked"
        status = messages.ERROR
    else:
        response = Likes.objects.create(
            post=post,
            user=request.user
        )
        # Return to home page
        message = "Successfully liked post."
        status = messages.SUCCESS
    messages.add_message(request, status, message)
    return redirect("index")


@login_required
def unlike(request, post_id):
    post = Post.objects.get(pk=post_id)
    existing = Likes.objects.filter(
        post=post,
        user=request.user
    )
    if not existing:
        message = "Post not liked before"
        status = messages.ERROR
    else:
        existing.delete()
        # Return to home page
        message = "Successfully unliked post."
        status = messages.SUCCESS
    messages.add_message(request, status, message)
    return redirect("index")


@login_required
def create_post(request):
    if request.method == "POST":
        # Create post
        response = Post.objects.create(
            text=request.POST['post_text'],
            user=request.user
        )
        # Return to home page
        message = "Successfully created a new post."
        messages.add_message(request, messages.SUCCESS, message)
        return redirect("index")
    return render(request, "network/post.html")


@login_required
def edit_post(request, post_id):
    try:
        post = Post.objects.get(user=request.user, pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)
    if request.method == "POST":
        # Save post
        post.text = request.POST['post_text']
        post.save()
        # Return to home page
        message = "Successfully edited the post."
        messages.add_message(request, messages.SUCCESS, message)
        return redirect("index")
    return render(request, "network/post.html", {'post': post})


@login_required
def following_posts(request):
    # Return to home page with following flag True
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
            traceback.print_exc()
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
