import re
from venv import create
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from .models import Likes, User, Post, Followers
import datetime
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

def index(request):
    posts = Post.objects.all().order_by("-edited_at")
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/index.html",{"page_obj": page_obj})

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

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@login_required(login_url='login')
def newpost(request):
    if request.method == "POST":
        post = request.POST.get("post")
        if post != "":  
            user = request.user
            created_at = datetime.datetime.now()
            post = Post.objects.create(user=user, post=post, created_at = created_at, edited_at = created_at)
            post.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/newpost.html", {"message": "Please enter a post."})
    else:
        return render(request, "network/newpost.html")

def user(request, username):
    user = User.objects.get(username=username)
    posts = Post.objects.filter(user=user).order_by("-edited_at")
    followers = Followers.objects.filter(user=user).values('follower__username').distinct()
    followers_count = followers.count()
    following = Followers.objects.filter(follower=user).values('user').distinct()
    following_count = following.count()
    check_for_follower = followers.values_list('follower__username', flat=True)
    check_for_same = User.objects.filter(username=username).values_list('username', flat=True)
    if request.user.username in check_for_same or request.user.id == None:
        return render(request, "network/user.html",{"user_now": user, "posts": posts, "followers": followers_count, "following": following_count, "can_follow": False})
    if request.user.username in check_for_follower:
        return render(request, "network/user.html",{"user_now": user, "posts": posts, "followers": followers_count, "following": following_count, "can_follow": True, "followed": True})
    else:
        return render(request, "network/user.html",{"user_now": user, "posts": posts, "followers": followers_count, "following": following_count, "can_follow": True, "followed": False})

@login_required(login_url='login')
def follow(request, username):
    user = User.objects.get(username=username)
    follower = User.objects.get(id=request.user.id)
    instance = Followers(user=user)
    instance.save()
    instance.follower.add(follower)
    return HttpResponseRedirect(reverse("user", args=[username]))

@login_required(login_url='login')
def unfollow(request, username):
    user = User.objects.get(username=username)
    follower = User.objects.get(id=request.user.id)
    Followers.objects.filter(user=user, follower=follower).delete()
    return HttpResponseRedirect(reverse("user", args=[username]))

@login_required(login_url='login')
def following(request):
    following = Followers.objects.filter(follower=request.user).values('user').distinct()
    posts = Post.objects.filter(user__in=following).order_by("-edited_at")
    return render(request, "network/following.html", {"posts": posts})

@login_required(login_url='login')
def editpost(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.method == "POST":
        post.post = request.POST.get("post")
        if post.post != "": 
            post.edited_at = datetime.datetime.now()
            post.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/editpost.html", {"message": "Please enter something."})
    return render(request, "network/editpost.html", {"post": post})

@login_required(login_url='login')
def like(request, post_id):
    post = Post.objects.get(id=post_id)
    user = User.objects.get(id=request.user.id)
    posts = Post.objects.all().order_by("-edited_at")
    paginator = Paginator(posts, 2) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    if Likes.objects.filter(post=post, user=user).exists():
        Likes.objects.filter(post=post, user=user).delete()
        post.likes -= 1
        post.save()
        # return JsonResponse({"likes": post.likes})
        return HttpResponseRedirect(reverse("index"))
    else:
        instance = Likes(user=user, post=post)
        instance.save()
        post.likes += 1
        post.save()
        # return JsonResponse({"likes": post.likes})
        return HttpResponseRedirect(reverse("index"))