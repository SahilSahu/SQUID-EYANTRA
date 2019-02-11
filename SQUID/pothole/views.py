'''Importing necessary modules from python and django library'''

from django.shortcuts import render
from django.conf import settings
from pothole import views
from .models import *
from django.shortcuts import redirect
from django.contrib.auth import authenticate,login
from django.contrib.auth import views as auth_views
from django.views.generic import View
from django.http import HttpResponse
from statistics import mean
import csv
from array import *
import re
import os
import numpy as np
import math
import pylab
from random import randint
from django.views.generic import TemplateView
from chartjs.views.lines import BaseLineChartView

"""/* A function to store x,y,z values from the csv generated /*"""
def xyzValues():
	with open(os.path.join(settings.MEDIA_ROOT,"data1_0.csv"), 'r') as k:
		data = [d for d in list(csv.reader(k, delimiter=',')) if d != []]
		print(data[0][0])
		t = [float(data[i][0]) for i in range(len(data)) if data[i][0]!='']
		x = [float(data[i][1]) for i in range(len(data)) if data[i][1]!='']
		y = [float(data[i][2]) for i in range(len(data)) if data[i][2]!='']
		z = [float(data[i][3]) for i in range(len(data)) if data[i][3]!='']

		return [t,x,y,z]

"""/* Classes to implement visualization by django-chartjs*/"""
class LineChartJSONView(BaseLineChartView):
	def get_labels(self):
		t,x,y,z = xyzValues()
		return t

	def get_providers(self):
		return ["x-axis","y-axis","z-axis"]

	def get_data(self):
		t,x,y,z = xyzValues()
		return [x,y,z]

class LineChartJSONViewRide(BaseLineChartView):
	def get_labels(self):
		t,x,y,z = xyzValues()
		return t

	def get_providers(self):
		return ["Ride-Quality_Score"]
	def get_data(self):
		t,x,y,z = xyzValues()
		score=[]
		for i in range(len(x)):
			score.append(math.sqrt((x[i]**2 + y[i]**2 + z[i]**2)))
		return [score]

class RadarChartJSONViewRide(BaseLineChartView):
	def get_labels(self):
		return ["High","Medium","Low"]

	def get_providers(self):
		return ["High Count","Medium Count","Low Count"]
	def get_data(self):
		hc,mc,lc = [],[],[]
		for i in range(0,100,10):
			hc.append(i)
		for j in range(0,70,10):
			mc.append(j)
		for k in range(0,82,10):
			lc.append(i)
		# score = float(score)
		return [[76,0,0],[0,82,0],[0,0,63]]


'''/* Implementing visualization */'''
line_chart = TemplateView.as_view(template_name='pothole/analytics.html')
line_chart_json = LineChartJSONView.as_view()

line_chart_json_ride = LineChartJSONViewRide.as_view()

radar_chart_json = RadarChartJSONViewRide.as_view()

'''/* Function to validate login */'''
def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                return redirect('/dashboard')
            else:
                return render(request, 'pothole/index.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'pothole/index.html', {'error_message': 'Invalid login'})
    return render(request, 'pothole/index.html')

'''/* Function to logout */'''
def logout_user(request):
    logout(request)
    return render(request, 'pothole/index.html')



'''/* Function to render dashboard */'''
def index(request):
 	return render(request,'pothole/index.html')

# Routes
# 1. Not logged in:
	# check if logged in: /check
	# if authenticated go to /dashboard
	# else /loginpage
def check(request):
	print("I m chcek")
	if request.session.has_key('username'):
		print("I m authenticated")
		return render(request,'pothole/dashboard.html')
	else:
		return render(request,'pothole/login.html')


def login(request):
	return render(request,'pothole/dashboard.html')


def logout(request):
    return render(request,'pothole/index.html')


'''/* Function to render dashboard */'''
def dashboard(request):
	return render(request,'pothole/dashboard.html')

'''/* Function to render analytics */'''
def analytics(request):
	return render(request,'pothole/analytics.html')

'''/* Function to  generate colorcode based on ride quality score */'''
def getcolorcode(score):
	if score >=8.381720005464272 and score <=8.63253751062201:
		color = '#003300'
	elif score >8.63253751062201 and score <=8.883355015779747:
		color = '#009900'
	elif score >8.883355015779747 and score <=9.134172520937485:
		color = '#00CC33'
	elif score >9.134172520937485 and score <=9.384990026095222:
		color = '#CC9900'
	elif score >9.384990026095222 and score <=9.63580753125296:
		color = '#CCCC00'
	elif score >9.63580753125296 and score <=9.886625036410697:
		color = '#CCFF00'
	elif score >9.886625036410697 and score <=10.137442541568435:
		color = '#880000'
	elif score >10.137442541568435 and score <=10.388260046726172:
		color = '#580000'
	else:
		color = '#380000'
	return color

'''/* Function to display ride quality on google maps */'''
def map(request):
    data = PolylineData.objects.all()

    os.chdir(settings.MEDIA_ROOT)
    locations = []
    for f in data:
        with open('{}\\'.format(settings.MEDIA_ROOT) + f.filename) as k:
            all_data = list(csv.reader(k , delimiter=','))

        i=0
        for m in range(0, len(all_data), 20):
            with open('{}\\'.format(settings.MEDIA_ROOT) + f.filename.rstrip('.csv') + '_{}.csv'.format(i), 'w+') as t:
                w = csv.writer(t, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                for row in all_data[m:m+21]:
                    w.writerow(row)
                i+=1

    f = [f for f in os.listdir(settings.MEDIA_ROOT) if re.search(r'.*_.*\.csv$',f)]

    for everyfile in f:
        with open(everyfile, 'r') as k:
            lis = []
            locationcol = {}
            data = [d for d in list(csv.reader(k , delimiter=',')) if d!=[]]
            print(data)
            print(mean([float(data[i][1]) for i in range(len(data)) if data[i][1]!='']))
            """/* Calculating mean of data to eliminate noise*/"""
            x = mean([float(data[i][1]) for i in range(len(data)) if data[i][1]!=''])
            y = mean([float(data[i][2]) for i in range(len(data)) if data[i][2]!=''])
            z = mean([float(data[i][3]) for i in range(len(data)) if data[i][3]!=''])

            #<!---Calculating ride quality score !--->
            score = math.sqrt((x**2 + y**2 + z**2))

            latitude = [float(data[i][4]) for i in range(len(data)) if data[i][4]!='']
            longitude = [float(data[i][5]) for i in range(len(data)) if data[i][5]!='']
   			"""Zipping the contents"""
            for lat,longi in zip(latitude, longitude):
                lis.append({"lat": lat, "lng": longi})

            locationcol['location'] = lis
            locationcol['color'] = getcolorcode(score)
            locations.append(locationcol)

    context = {
        'locations': locations
    }
    return render(request,'pothole/map.html', context)


"""/*Treshold algorithm to detect pothole*/"""
def thresholding_algo(y, lag, threshold, influence):
    signals = np.zeros(len(y))
    filteredY = np.array(y)
    avgFilter = [0]*len(y)
    stdFilter = [0]*len(y)
    avgFilter[lag - 1] = np.mean(y[0:lag])
    stdFilter[lag - 1] = np.std(y[0:lag])
    for i in range(lag, len(y) - 1):
        if abs(y[i] - avgFilter[i-1]) > threshold * stdFilter[i-1]:
            if y[i] > avgFilter[i-1]:
                signals[i] = 1
            else:
                signals[i] = -1

            filteredY[i] = influence * y[i] + (1 - influence) * filteredY[i-1]
            avgFilter[i] = np.mean(filteredY[(i-lag):i])
            stdFilter[i] = np.std(filteredY[(i-lag):i])
        else:
            signals[i] = 0
            filteredY[i] = y[i]
            avgFilter[i] = np.mean(filteredY[(i-lag):i])
            stdFilter[i] = np.std(filteredY[(i-lag):i])

    print(np.asarray(signals))
    return dict(signals = np.asarray(signals),
                avgFilter = np.asarray(avgFilter),
                stdFilter = np.asarray(stdFilter))


"""/* Pinpointing pothole locations */"""
def locations(request):
	locations=[]
	os.chdir(settings.MEDIA_ROOT)
	f = [f for f in os.listdir(settings.MEDIA_ROOT) if re.search(r'.*_.*\.csv$',f)]

	for everyfile in f[:5]:
		with open(everyfile, 'r') as k:
		    data = [d for d in list(csv.reader(k, delimiter=',')) if d != []]
		    lis=[]
		    locationcol = {}
		    lati_l = []
		    longi_l =[]
		    y = np.array([float(data[i][3]) for i in range(len(data)) if data[i][3]!=''])
		    lat = np.array([float(data[i][4]) for i in range(len(data)) if data[i][4]!=''])
		    lon = np.array([float(data[i][5]) for i in range(len(data)) if data[i][5]!=''])
		    # Settings: lag = 30, threshold = 5, influence = 0
		    lag = 2
		    threshold = 3
		    influence = 2

		    # Run algo with settings from above
		    result = thresholding_algo(y, lag=lag, threshold=threshold, influence=influence)

		    #map entries
		    for i in range(0,len(result["signals"])):
		    	if(result["signals"][i] == 1 or result["signals"][i] == -1):
		    		lati_l.insert(i,lat[i])
		    		longi_l.insert(i,lon[i])

		    for lat,longi in zip(lati_l, longi_l):
		    	lis.append({"lat": lat, "lng": longi})

		    locationcol['location'] = lis
		    locations.append(locationcol)
	context = {
        'locations': locations
    }
	return render(request,'pothole/locations.html',context)