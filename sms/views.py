from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib.auth.models import User
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from sms.forms import AuthenticateForm, UserCreateForm, ServerForm
from sms.models import Server


def index(request, auth_form=None, user_form=None):
    # User is logged in
    if request.user.is_authenticated():
        server_form = ServerForm()
        user = request.user
        ribbits_self = Server.objects.filter(user=user.id)
        return render(request,
                      'buddies.html',
                      {'server_form': server_form, 'user': user,
                       'next_url': '/', })
    else:
        # User is not logged in
        auth_form = auth_form or AuthenticateForm()
        user_form = user_form or UserCreateForm()

        return render(request,
                      'home.html',
                      {'auth_form': auth_form, 'user_form': user_form, })


def login_view(request):
    if request.method == 'POST':
        form = AuthenticateForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            # Success
            return redirect('/')
        else:
            # Failure
            return index(request, auth_form=form)
    return redirect('/')


def logout_view(request):
    logout(request)
    return redirect('/')


def signup(request):
    user_form = UserCreateForm(data=request.POST)
    if request.method == 'POST':
        if user_form.is_valid():
            username = user_form.clean_username()
            password = user_form.clean_password2()
            user_form.save()
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/')
        else:
            return index(request, user_form=user_form)
    return redirect('/')


@login_required
def public(request, server_form=None):
    server_form = server_form or ServerForm()
    server_names = Server.objects.get('server_name')
    print server_names
    return render(request,
                  'public.html',
                  {'ribbit_form': server_form, 'next_url': '/ribbits',
                   'ribbits': server_names, 'username': request.user.username})


@login_required
def submit(request):
    ctx={}
    if request.method == "POST":
        server_form = ServerForm(data=request.POST)
        next_url = request.POST.get("next_url", "/")
        if server_form.is_valid():
            ribbit = server_form.save(commit=False)
            ribbit.user = request.user
            ribbit.save()
            return redirect(next_url,)
        else:
            return public(request, server_form)
    return redirect('/')


def get_latest(user):
    try:
        return user.ribbit_set.order_by('id').reverse()[0]
    except IndexError:
        return ""


@login_required
def users(request, username="", ribbit_form=None):
    if username:
        # Show a profile
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404
        ribbits = Server.objects.filter(user=user.id)
        if username == request.user.username or request.user.profile.follows.filter(user__username=username):
            # Self Profile
            return render(request, 'user.html', {'user': user, 'ribbits': ribbits, })
        return render(request, 'user.html', {'user': user, 'ribbits': ribbits, 'follow': True, })
    users = User.objects.all().annotate(ribbit_count=Count('ribbit'))
    ribbits = map(get_latest, users)
    obj = zip(users, ribbits)
    ribbit_form = ribbit_form or ServerForm()
    return render(request,
                  'profiles.html',
                  {'obj': obj, 'next_url': '/users/',
                   'ribbit_form': ribbit_form,
                   'username': request.user.username, })


@login_required
def follow(request):
    if request.method == "POST":
        follow_id = request.POST.get('follow', False)
        if follow_id:
            try:
                user = User.objects.get(id=follow_id)
                request.user.profile.follows.add(user.profile)
            except ObjectDoesNotExist:
                return redirect('/users/')
    return redirect('/users/')
