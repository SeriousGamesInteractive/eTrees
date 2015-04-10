# Create your views here.
import os
import sys
import json
import shutil
from unipath import Path
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render,redirect


def requestGame(request, code):
	return render(request,'publishstory/publish_new_user.html',{})