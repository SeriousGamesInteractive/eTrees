__author__ = 'Felix Rubio (at) SGI'

# Create your views here.
import csv
import os
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from eTrees.utils import returnAdmin
from eTrees.global_constants import Constants
from account.models import Trainer
from createstory.models import Project
from .models import UserGame, ProjectValoration

class CSVheaders(object):
	#Enum to represent the read of the import csv user 
	name = 0
	surname = 1
	username = 2
	email = 3
	sex = 4
	personid = 5
	additionalinfo = 6


@login_required(login_url='/login')
def PublishMenuView(request):
	'''
	Handles the view of the published stories
	'''

	projects = Project.objects.filter(activate = Constants.ACTIVATE_PUBLISH, user__id = request.user.id)
	currentUserId = request.user.id
	isTrainerModel = Trainer.objects.filter(user__id = currentUserId)
	for project in projects:
		canDelete = False
		if len(isTrainerModel) > 0:
			if isTrainerModel[0].user.id == project.owner_id: #Has rights to delete the library
				canDelete = True
		else:
			canDelete = True
		project.canDelete = canDelete
	return render(request,'publishstory/publishmenu.html',{"stories":projects})

@login_required(login_url='/login')
def PublishNewUserView(request):
	'''
	Manage the creation of a new trainee in the system. There are two ways of creating a trainee:
		- Using the html form
		- Importing a CSV file with the information of several users
	'''
	if request.method == "POST":
		if request.FILES.get('file_import'): # Import form			
			fileupload = request.FILES['file_import']
			filename, fileExt = os.path.splitext(fileupload.name)
			if "csv" not in fileExt:
				pass # TODO finish the return message when the file is incompatible	
			#Create the xml file for the respective library created 
			result = importUserCsv(fileupload)
			#If the return is a number the import has been a success. Otherwise, it returns the error of the import
			if isinstance(result,(int,long,float)):
				return render(request,'publishstory/publish_new_user.html',{"message_success": str(result)+" users have been imported."})
			return render(request,'publishstory/publish_new_user.html',{"message_import_error":result})
				
		else: # create new user form

			#Control of the form.
			name = ""
			if request.POST.get('name'):
				name = request.POST['name']
			else:
				return render(request,'publishstory/publish_new_user.html',{"message_import_error":"Field name cannot be empty"})
			surname = ""
			if request.POST.get('surname'):
				surname = request.POST['surname']
			else:
				return render(request,'publishstory/publish_new_user.html',{"message_import_error":"Field surname cannot be empty"})
			username = ""
			if request.POST.get('username'):
				username = request.POST['username']
			else:
				return render(request,'publishstory/publish_new_user.html',{"message_import_error":"Field username cannot be empty"})		
			email = ""
			if request.POST.get('email'):
				email = request.POST['email']
			else:
				return render(request,'publishstory/publish_new_user.html',{"message_import_error":"Field email cannot be empty"})		
			sex = ""
			if request.POST.get('sex'):
				sex = request.POST['sex']
			else:
				return render(request,'publishstory/publish_new_user.html',{"message_import_error":"Field sex cannot be empty"})		
			personid = request.POST['personid']
			checkUser = UserGame.objects.filter(username=username)
			if len(checkUser) > 0 :
				return render(request,'publishstory/publish_new_user.html',{"message_import_error":"Username: "+username + " already exits in the system."})				
			checkEmail = UserGame.objects.filter(email = email)
			if len(checkEmail) > 0:
				return render(request,'publishstory/publish_new_user.html',{"message_import_error":"Email: "+email + " already exits in the system."})
			if personid == "":
				personid = 0
			try:
   				validPersonid = int(personid)
			except ValueError:
   				return render(request,'publishstory/publish_new_user.html',{"message_import_error":"Company ID must be a number."})
			#birthday = request.POST['bdate']			
			additionalinfo = request.POST['additionalinfo']
			userCreated = UserGame(name = name, surname = surname,username =username, email = email,sex = sex,
				personid = validPersonid,additionalinfo = additionalinfo)
			userCreated.save()
			#Give the access to the group of admin that has created the user
			userAdmin = returnAdmin(request.user)
			userCreated.user.add(userAdmin)
			return render(request,'publishstory/publish_new_user.html',{"message_success":"User: "+username + " has been created."})
	return render(request,'publishstory/publish_new_user.html',{})

def importUserCsv(filepath):
	'''
		Get the databa from a csv file.
		CSV format:
			name*    surname*    username*    email*    sex*   personid    additionalinfo
		*this fields are mandatories.

		Save the data obtained from the csv into the database Usergame
	'''
	userGames=[]
	dataReader = csv.reader(filepath, delimiter=',',quotechar='"')
	print "CSV: ",dataReader
	for row in dataReader:
		if row[0].lower() != 'name': # ignore the first line of the csv file
			try:
				userGame = UserGame()				
				userGame.name = row[CSVheaders.name]
				if not userGame.name:
					return "The name field in line %d cannot be empty." % (len(userGames) + 2)
				userGame.surname = row[CSVheaders.surname]
				if not userGame.surname:
					return "The surname field in line %d cannot be empty." % (len(userGames) + 2)
				#username is an unique field
				userGame.username = row[CSVheaders.username]
				if not userGame.username:
					return "The username field in line %d cannot be empty." % (len(userGames) + 2)									
				#Check if the useranme is already in use
				check_username = UserGame.objects.filter(username = userGame.username)
				if len(check_username) > 0:
					return "The username %s in the line %d is already in use " % (userGame.username, len(userGames) + 2)
				userGame.email = row[CSVheaders.email]
				if not userGame.email:
					return "The email field in line %d cannot be empty." % (len(userGames) + 2)
				check_email = UserGame.objects.filter(email = userGame.email)
				if len(check_email) > 0:
					return "The email %s in the line %d is already in use " % (userGame.email, len(userGames) + 2)
				userGame.sex = row[CSVheaders.sex]
				if not userGame.sex:
					return "The sex field in line %d cannot be empty." % (len(userGames) + 2)
				print "header personid: ",row[CSVheaders.personid]
				personid = 0
				if str(row[CSVheaders.personid]) != "":
					personid = int(row[CSVheaders.personid])
				userGame.personid =  personid
				userGame.additionalinfo = row[CSVheaders.additionalinfo]
				userGames.append(userGame)
			except Exception as e:
				return "An error has ocurred: \n%s" % ( str(e))
	for userGame in userGames:
		try:
			userGame.save()
			userAdmin = returnAdmin(request.user)
			userGame.user.add(userAdmin)
		except Exception as e:
			return "An error has ocurred saving the database: \n%s" % (str(e))

	return len(userGames)

def PublishInviteUserView(request):
	'''
	View to show the stories published and the users to be invited. 
	'''
	userAdmin = returnAdmin(request.user)
	users = UserGame.objects.filter(user__id=userAdmin.id)
	projects = Project.objects.filter(activate = Constants.ACTIVATE_PUBLISH, user__id = request.user.id)
	projectValorations = []
	for project in projects:
		projectValorations.append(len(ProjectValoration.objects.filter(project__id = project.id)))
	zipped = zip(projects,projectValorations) #Include in one variable the information of two queryset.

	return render(request,'publishstory/publish_invite_user.html',{"zipped":zipped,"users":users})	


def PublishReporting(request):
	"""
	View in charge of showing the reporting of the stories
	"""
	publishStories = Project.objects.filter(activate =  Constants.ACTIVATE_PUBLISH , user__id = request.user.id)

	completedPublishStories = []
	for publishStory in publishStories:
		isProjectValorationCompleted = ProjectValoration.objects.filter(completed = True, project__id = publishStory.id)
		if len(isProjectValorationCompleted) > 0:
			completedPublishStories.append(publishStory)
	return render(request,'publishstory/publish_reporting.html',{"completeStories":completedPublishStories})
