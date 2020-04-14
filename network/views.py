from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
import traceback
from .models import *
from .serializers import *

from datetime import datetime


@login_required
def index(request, following=False, message=None, error=None):
    if following:
        following_users = request.user.followers.all()
        # following_users = UserSerializer().get_followers(request.user)
        posts = Post.objects.filter(user__id__in=following_users)
    else:
        posts = Post.objects.all()

    # #Prepare UI data
    ui_data = list()
    for post in posts:
        likes = Likes.objects.filter(post=post).count()
        ui_data.append({
            'post_text': post.text,
            'posted_by': post.user,
            'posted_at': post.created_at,
            'likes_count': likes
        })

    # #UI Params
    params = {
        'rows': ui_data,
        'message': message,
        'error': error
    }
    return render(
        request,
        "network/index.html",
        params
    )


@login_required
def user_info(request, user_id):
    user = User.objects.get(pk=user_id)
    following_users = user.following.count()
    followers = user.followers.count()
    posts = Post.objects.filter(user=user)

    """
    If clicked user is not session user,
    find out if this session session has followed this clicked user,
    if no, should be allowed to follow else should be allowed to unfollow
    """
    has_followed = None
    if not user == request.user:
        if request.user in followers:
            has_followed = True
        else:
            has_followed = False

    # #Build UI Params
    params = {
        'user': user,
        'following_count': following_users,
        'follwers_count': followers,
        'posts': posts,
        'has_followed': has_followed
    }
    return render(request, "network/user_info.html", params)


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
        return index(request, message=message)
    return render(request, "network/create_post.html")


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
