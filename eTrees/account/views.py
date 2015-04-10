# Create your views here.
from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.views.generic import  RedirectView
from django.core.urlresolvers import reverse
from eTrees.global_constants import Constants
from .models import Trainer
from createstory.models import Project
from library.models import ResourcesLibrary

def loginView(request):
	request.session.test_cookie_worked()
	print "Session" ,request.session
	if request.method == 'POST':		
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password = password)
		if user is not None:
			if user.is_active:
				login(request,user)
				print "POST ", request.POST
				if request.POST.has_key('remember_me'):   
					request.session.set_expiry(1209600)
					print "session: ", request.session
				return redirect('admin_menu')
			else:
				# Return diabled account
				return HttpResponseRedirect("/?error='not active'")
		else:
			#Return invalid login
			return HttpResponseRedirect("/?error='invalid'")
	return render(request,'account/login.html',{})

@login_required(login_url='/login')
def menuView(request):
    return render(request,'account/menu.html',{})

@login_required(login_url='/login')
def accountView(request):

	isTrainer = False

	trainerUser = Trainer.objects.filter(user__id = request.user.id)
	if len(trainerUser) > 0:
		isTrainer = True
	type=""
	if request.method == "POST":		
		name = request.POST['name']
		surname = request.POST['surname']
		username = request.POST['username']
		password = request.POST['password']		
		if 'change-user' in request.POST: 
			#Form to modify current user settings
			type="loginuser"
			currentpassword = request.POST['currentpassword']
			if not request.user.check_password(currentpassword):
				return render(request,'account/admin_account.html',
					{"userLogin":request.user,"type":type,"istrainer":isTrainer,"loginmessage":"The password provided is not correct."}) 
			if not username == request.user.username and User.objects.filter(username=username).exists():
				return render(request,'account/admin_account.html',{"userLogin":userLogin,"type":type,"istrainer":isTrainer,"loginmessage":"Username already exists."})
			request.user.first_name = name
			request.user.last_name = surname
			request.user.username = username
			request.user.set_password(password)
			request.user.save()
			return render(request,'account/admin_account.html',{"userLogin":request.user,"type":type,"istrainer":isTrainer, "message":"User %s has been modified" % (username)})
		elif 'create-trainer' in request.POST:
			type="createtrainer"
			if User.objects.filter(username=username).exists():
				#send error
				return render(request,'account/admin_account.html',{"userLogin":username,"type":type,"istrainer":isTrainer,"message_user":"Username already exists."})
			djangoUser = User.objects.create_user(username = username,password = password,first_name = name, last_name = surname)
			djangoUser.save()
			adminModel = request.user
			if Trainer.objects.filter(user__id = request.user.id).exists():
				adminModel = Trainer.objects.get(user__id = request.user.id).admin
			trainer = Trainer(user=djangoUser,admin=adminModel,trainer= True)
			trainer.save()
			listProject = Project.objects.filter(user__id = adminModel.id)

			listStoriesAllow = request.POST.getlist('stories')
			for storyId in listStoriesAllow:
				story = Project.objects.get(id=storyId)
				story.user.add(djangoUser)
			#Add the user to all the projects and libraries created 
			#projects = Project.objects.all()
			#for project in projects:
			#	project.user.add(djangoUser)
			listLibrariesAllow = request.POST.getlist('libraries')		
			for libId in listLibrariesAllow:
				library = ResourcesLibrary.objects.get(id=libId)
				library.user.add(djangoUser)

			#Add the stories to the trainer
			#for story in listProject:				
			#	story.user.add(djangoUser)

			#listLibrary = ResourcesLibrary.objects.filter(user__id = adminModel.id)
			#Add the stories to the trainer
			#for library in listLibrary:				
			#	library.user.add(djangoUser)			
			return render(request,'account/admin_account.html',{"userLogin":request.user,"type":type,"istrainer":isTrainer, "message":"New user %s has been created!!" % (username)})	
		else:
			type="createuser"
			if User.objects.filter(username=username).exists():
				#send error
				return render(request,'account/admin_account.html',{"userLogin":username,"type":type,"istrainer":isTrainer,"message_user":"Username already exists."})
			djangoUser = User.objects.create_user(username = username,password = password,first_name = name, last_name = surname)
			djangoUser.save()
			#Add the stories allowed to the user
			listStoriesAllow = request.POST.getlist('stories')
			for storyId in listStoriesAllow:
				story = Project.objects.get(id=storyId)
				story.user.add(djangoUser)
			#Add the user to all the projects and libraries created 
			#projects = Project.objects.all()
			#for project in projects:
			#	project.user.add(djangoUser)
			listLibrariesAllow = request.POST.getlist('libraries')		
			for libId in listLibrariesAllow:
				library = ResourcesLibrary.objects.get(id=libId)
				library.user.add(djangoUser)
			return render(request,'account/admin_account.html',{"userLogin":request.user,"type":type,"istrainer":isTrainer, "message":"New user %s has been created!!" % (username)})	
	userProjectsNoPublish = Project.objects.filter(user__id = request.user.id, activate= Constants.ACTIVATE_UNPUBLISH)
	userProjectsPublish = Project.objects.filter(user__id = request.user.id, activate= Constants.ACTIVATE_PUBLISH)
	userLibrary = ResourcesLibrary.objects.filter(user__id = request.user.id)
	return render(request,'account/admin_account.html',{"userLogin":request.user,"type":type,"istrainer":isTrainer, "userstories_nopublish":userProjectsNoPublish,"userstories_publish":userProjectsPublish, "library_user":userLibrary})


class LogoutView(RedirectView):
    def get(self, request, *args, **kwargs):
        logout(request)
        return super(LogoutView, self).get(request, args, **kwargs)
    
    def get_redirect_url(self, **kwargs):
        return reverse("login")
	



