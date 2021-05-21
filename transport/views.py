from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import time
from django import forms
import json
from django.core.files.storage import FileSystemStorage

from .models import User, Response, Pay_method, Category, Type, Additional, Transport, Deal
from .forms import NewUserForm, LoginForm, NewTransportForm
# Create your views here.

def index(request):
    return render(request, 'transport/index.html')

def login_view(request):
    instance = {}
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
            instance['error'] = "Invalid username and/or password."
            return render(request, "transport/login.html", instance)

    instance['form'] = LoginForm()
    return render(request, "transport/login.html", instance)

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

def register(request):
    instance = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirmarion = request.POST['confirmation']
        email = request.POST['email']
        phone = request.POST['phone']

        if password != confirmarion:
            instance['error'] = "Passwords must match."
            return render(request, 'transport/login.html', instance)

        try:
            user = User.objects.create_user(username, email, password, phone=phone)
            #user.save()
        except IntegrityError:
            instance['error'] = "User already exists."
            return render(request, "network/register.html", instance)

        login(request, user)
        return HttpResponseRedirect(reverse('index'))

    instance['form'] = NewUserForm()
    return render(request, 'transport/register.html', instance)

def get_offers(request):

    # Get start and end points
    start = int(request.GET.get('start') or 0)
    end = int(request.GET.get('end') or (start + 9))

    # Generate lists of offers
    data = []
    for offer in Transport.objects.all().order_by('-timestamp'):
        offer_data = {
            'id': offer.pk,
            'name': offer.name,
            'description': offer.description,
            'price_per_day': offer.price_per_day,
            'photo': 'media/' + offer.photo.name,
            'timestamp': offer.timestamp
        }
        data.append(offer_data)

    # Artificially delay speed of response 
    time.sleep(1)

    # Return list of offers
    return JsonResponse({
        'offers': data
    }, status=200)

@login_required(login_url='login')
def add_offer(request):
    instance = {}
    
    if request.method == 'POST':
        form = NewTransportForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            category = Category.objects.get(pk=form.cleaned_data['category'])
            type = Type.objects.get(pk=form.cleaned_data['type'])
            price_per_day = form.cleaned_data['price_per_day']
            owner = request.user
            photo = request.FILES['photo']
            Transport.objects.create(name=name, description=description, category=category, type=type, price_per_day=price_per_day, owner=owner, photo=photo)
            instance['message'] = 'SUCCESS'
            return render(request, 'transport/add_offer.html', instance)
        instance['error'] = 'Invalid Input'
        return render(request, 'transport/add_offer.html', instance)
    instance['form'] = NewTransportForm()
    return render(request, 'transport/add_offer.html', instance)

def offer_view(request, offer_id):
    instance = {}
    offer = Transport.objects.get(pk=offer_id)
    instance['offer'] = offer
    return render(request, 'transport/offer_page.html', instance)
