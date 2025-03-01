# Uncomment the required imports before adding the code
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from datetime import datetime

from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .populate import initiate

from .models import CarMake, CarModel
from .restapis import get_request, analyze_review_sentiments, post_review

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    data = {"userName":""}
    return JsonResponse(data)
# ...

# Create a `registration` view to handle sign up request
@csrf_exempt
def registration(request):
    context = {}
    data = json.loads(request.body)
    username_exist = False

    try:
        # Check if user already exists
        User.objects.get(username=data['userName'])
        username_exist = True
    except:
        # If not, simply log this is a new user
        logger.debug("{} is new user".format(data['userName']))

    # If it is a new user
    if not username_exist:
        # Create user in auth_user table
        user = User.objects.create(username=data['userName'], first_name=data['firstName'], last_name=data['lastName'], password=data['password'], email=data['email'])

        # Login the user and redirect to list page
        login(request, user)

        dato = {"userName":data['userName'],"status":"Authenticated"}
        return JsonResponse(dato)
    else:
        dato = {"userName":data['userName'],"error":"Already Registered"}
        return JsonResponse(dato)
    
def get_cars(request):
    count = CarMake.objects.filter().count()
    print(count)

    if (count == 0):
        initiate()
    
    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for car_model in car_models:
        cars.append({"CarModel": car_model.Name, "CarMake": car_model.car_make.Name})
    
    return JsonResponse({"CarModels": cars})

#Update the `get_dealerships` render list of dealerships all by default, particular state if state is passed
def get_dealerships(request, state="All"):
    if(state == "All"):
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/"+state
    dealerships = get_request(endpoint)
    return JsonResponse({"status":200,"dealers":dealerships})

'''
takes the dealer_id as a parameter in views.py 
and add a mapping urls.py. It will use the get_request you implemented in the restapis.py passing the /fetchDealer/<dealer id> endpoint.
'''
def get_dealer_details(request, dealer_id):
    if(dealer_id):
        endpoint = "/fetchDealer/"+str(dealer_id)
        dealership = get_request(endpoint)
        return JsonResponse({"status":200,"dealer":dealership})
    else:
        return JsonResponse({"status":400,"message":"Bad Request"})

'''
takes the dealer_id as a parameter in views.py and add a mapping urls.py. 
It will use the get_request you implemented in the restapis.py passing the /fetchReviews/dealer/<dealer id> endpoint. 
It will also call analyze_review_sentiments in restapis.py to consume the microservice and determine the sentiment of each of the reviews and set the value in the review_detail dictonary which is returned as a JsonResponse.
'''
def get_dealer_reviews(request, dealer_id):
    # if dealer id has been provided
    if(dealer_id):
        endpoint = "/fetchReviews/dealer/"+str(dealer_id)
        reviews = get_request(endpoint)
        for review_detail in reviews:
            response = analyze_review_sentiments(review_detail['review'])
            print(response)
            review_detail['sentiment'] = response['sentiment']
        return JsonResponse({"status":200,"reviews":reviews})
    else:
        return JsonResponse({"status":400,"message":"Bad Request"})

'''
First check if user is authenticated because only authenticated users can post reviews for a dealer.
Call the post_request method with the dictionary
Return the result of post_request to add_review view method. You may print the post response
Return a success status and message as JSON
Configure the route for add_review view in url.py.
'''
def add_review(request):
    if(request.user.is_anonymous == False):
        data = json.loads(request.body)
        try:
            response = post_review(data)
            return JsonResponse({"status":200})
        except:
            return JsonResponse({"status":401,"message":"Error in posting review"})
    else:
        return JsonResponse({"status":403,"message":"Unauthorized"})