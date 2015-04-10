__author__ = 'Felix Rubio (at) SGI'

# Create your views here.
import os
import json
from unipath import Path
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from django.conf import settings
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from eTrees.global_constants import Constants
from account.models import Trainer
from library.models import ResourcesLibrary
from api.utils import getExtendedPath, recalculateTree
from .models import Project, Node, Attribute, ClosureTable, Category
from .utils import parseXMLNode, deleteContentStory, updateTreeJsonName, resultTemplate, validateCreateEditStoryForm, updateColorOptionNode


@login_required(login_url='/login')
def EditStoryMenuView(request):
	'''
		Render the page edit story menu and it manages the form to create a new story.
		The render sends as parameter the list of stories already created and the libraries already created
	'''
	projects = Project.objects.filter(user__id__exact=request.user.id,activate = Constants.ACTIVATE_UNPUBLISH)	
	libraries = ResourcesLibrary.objects.filter(user__id__exact = request.user.id)
	if request.method == 'POST':
		storyId = request.POST["story_id"]
		return redirect('create_copy_story',story=storyId)		
	return render(request,'createstory/editstorymenu.html',{'projects':projects,'libraries':libraries})

@login_required(login_url='/login')
def CreateCopyStory(request,story):
	'''
		Make the copy of all the content of one story to a new one
		Check the type of user who wants to copy the story (Trainer or Admin) and assign the ownership of the story to that user.
		Finally, validate the story with the method validateCreateEditStoryForm

		parameters:
			request
			story -> id of the project to be copied
	'''
	project = Project.objects.get(id = story)
	libraries = ResourcesLibrary.objects.filter(user__id__exact = request.user.id).exclude(pk__in=project.resourceslibrary.all())
	trainers = Trainer.objects.filter(admin__id = request.user.id)
	trainerUser = Trainer.objects.filter(user__id = request.user.id)
	categories = Category.objects.filter(project__id = story)

	if len(trainerUser) > 0:
		trainers = Trainer.objects.filter(admin__id = trainerUser[0].admin.id).exclude(id = trainerUser[0].id)
	if request.method == 'POST':
		
		#Cancel button back to the previous page
		if request.POST.get('cancel-story') != None:
			return redirect('admin_edit_story_menu')

		#----------------------------------------------------------------------------------
		#Call the method validateCreateStoryForm with the request, the trainerUSer, the project queryset and the flag to indicate the story has to be duplicated
		response = validateCreateEditStoryForm(request, trainerUser, project,categories, True)

		if response["status"] == 'error':
			return render(request,'createstory/editstory_form.html',{'project':project, 'categories':categories,
			 'libraries':libraries, "trainers":trainers, 'message':response["message"]})
		else:
			return redirect('admin_edit_story',story=response["project"])
		#----------------------------------------------------------------------------------
		
		#return render(request,'createstory/createstory_form.html',{'project':project,'categories':categories,'libraries':libraries,"trainers":trainers})
	return render(request,'createstory/editstory_form.html',{'header':"Copy story",'project':project,
		'categories':categories,'libraries':libraries,"trainers":trainers, 'template':"copy"})


@login_required(login_url='/login')
def CreateStoryForm(request):
	'''
	Show the form to create a new story, handling the saving of the library, categories and relevant information of the story

	'''
	libraries = ResourcesLibrary.objects.filter(user__id__exact = request.user.id)
	trainers = Trainer.objects.filter(admin__id = request.user.id)

	trainerUser = Trainer.objects.filter(user__id = request.user.id)
	if len(trainerUser) > 0:
		trainers = Trainer.objects.filter(admin__id = trainerUser[0].admin.id)	
	if request.method == 'POST':
		#Handle the submit of the form and pass the information to the method validateCreateEditStoryForm
		response = validateCreateEditStoryForm(request, trainerUser)

		if response["status"] == 'error':
			return render(request,'createstory/createstory_form.html',{'libraries':libraries,"trainers":trainers,
				'message':response["message"]})
		else:
			return redirect('admin_edit_story',story=response["project"])
		
	return render(request,'createstory/createstory_form.html',{'libraries':libraries,"trainers":trainers})

@login_required(login_url='/login')
def EditStoryForm(request,story):
	'''
		Allow to make modifications on a story already created.
	'''
	project = Project.objects.get(id = story, activate = Constants.ACTIVATE_UNPUBLISH)
	libraries = ResourcesLibrary.objects.filter(user__id__exact = request.user.id).exclude(pk__in=project.resourceslibrary.all())
	#Get the trainers not included on the story
	trainers = Trainer.objects.filter(admin__id = request.user.id).exclude(user__in = project.user.all())
	trainersIncluded = Trainer.objects.filter(user__id__in = project.user.all())
	trainerUser = Trainer.objects.filter(user__id = request.user.id)
	categories = Category.objects.filter(project__id = story)
	nodes = Node.objects.filter(project__id = story)
	if len(trainerUser) > 0: #Check if the current user has admin rights.
		#Get the trainers not included on the story from an user without admin rights
		trainers = Trainer.objects.filter(admin__id = trainerUser[0].admin.id).exclude(user__in = project.user.all())
	if request.method == 'POST':
		#Cancel button back to the previous page
		if request.POST.get('cancel-story') != None:
			return redirect('admin_edit_story',story=project.id)
		#Remove story
		if request.POST.get('delete-story') != None:
			#Check if the user is admin or the trainer has rights to delete the library
			currentUserId = request.user.id
			isTrainerModel = Trainer.objects.filter(user__id = currentUserId)
			canDelete = False
			if len(isTrainerModel) > 0:
				if isTrainerModel[0].user.id == project.owner_id: #Has rights to delete the library
					canDelete = True
			else:
				canDelete = True
			if canDelete:
				#Instead of deleting, we change the value activate of the project model
				#so it is not shown but the story still exists in the system.
				project.deactivateUnpublish()
				# Implementation of the deletion of the story for the sytem
				#deleteContentStory(project)
				#categories = Category.objects.filter(project__id = project.id)
				#categories.delete()
				#project.delete()
			else:
				return render(request,'createstory/editstory_form.html',{'project':project,'categories':categories,'libraries':libraries,"trainers":trainers,
				'trainersIncluded':trainersIncluded, 'template':"edit",'message':"You do not have rights to delete the story"})
			return redirect('admin_edit_story_menu')

		#-------------------------------------------------------------------	
		response = validateCreateEditStoryForm(request, trainerUser, project, categories)

		if response["status"] == 'error':
			return render(request,'createstory/editstory_form.html',{'project':project,'categories':categories,'libraries':libraries,"trainers":trainers,
		'trainersIncluded':trainersIncluded, 'template':"edit" , 'message':response["message"]})
		else:
			return redirect('admin_edit_story',story=response["project"])
		#--------------------------------------------------------------------	
	return render(request,'createstory/editstory_form.html',{'project':project,'categories':categories,'libraries':libraries,"trainers":trainers,
		'trainersIncluded':trainersIncluded, 'template':"edit" })


@login_required(login_url='/login')
def EditStoryView(request,story):
	'''
	Render the edit story page with the story selected on the edit story menu page
	Manage the creation of a new node.
	'''
	project = Project.objects.get(id=story, activate = Constants.ACTIVATE_UNPUBLISH)
	#Checking if the user log has accessed to this project
	flagAccess = False
	for user in project.user.all():
		if	user.id == request.user.id:
			flagAccess = True 
			pass
	if not flagAccess:
		return render(request,'404.html')
	nodes = Node.objects.filter(project__id = story)
	if request.method == 'POST':
		if request.POST.get('save-node') != None:
			#Controller to manage the creation of a new node
			if not bool(request.POST.get('name',False)):
				return render(request,'createstory/editstory.html',{'nodes':nodes,'story':project,
					'message':"You need to give a name to the node"})
			if not bool(request.POST.get('optionsNode',False)):
				return render(request,'createstory/editstory.html',{'nodes':nodes,'story':project,
					'message':"You need to select the type of node."})		
			#get the content of the form
			nodeName = request.POST['name']
			checkNameNode = Node.objects.filter(project__id = story, name = nodeName)
			if len(checkNameNode) > 0: #It is not allow to have to nodes with the same name
				return render(request,'createstory/editstory.html',{'nodes':nodes,'story':project,
					'message':"The name of the node already exist"})
			nodeDescription = request.POST['description']
			nodeType = request.POST['optionsNode']
			node = Node(name=nodeName,description=nodeDescription,type=nodeType,project = Project.objects.get(id=story),options=1)
			node.save()
			return redirect('admin_storybuilder',story=story,node=node.id)
		if request.POST.get('edit-node') != None:
			#Controller to manage the edition of a node
			if not bool(request.POST.get('name',False)):
				return render(request,'createstory/editstory.html',{'nodes':nodes,'story':project,
					'message':"You need to give a name to the node"})
			nodeName = request.POST['name']
			
			nodeDescription = request.POST['description']
			color = request.POST['colorpicker']
			nodeId = request.POST['editNodeId']
			node = Node.objects.get(id = nodeId)
			if node != None:
				checkNameNode = Node.objects.filter(project__id = story, name = nodeName).exclude(id = nodeId) #Check if other node has the same name
				if len(checkNameNode) > 0 : #It is not allow to have to nodes with the same name
					return render(request,'createstory/editstory.html',{'nodes':nodes,'story':project,
					'message':"The name of the node already exist"})
				node.name = nodeName
				node.description = nodeDescription
				node.color_option = color
				node.save()
				xmlFile = Path(settings.MEDIA_ROOT).child('stories').child(str(project.id)).child('node'+str(node.id)+'.xml')
				updateColorOptionNode(xmlFile,node.color_option)#change the color in the xml file
				treeJsonFile = Path(settings.MEDIA_ROOT).child('stories').child(str(project.id)).child('tree.json')	
				if os.path.exists(treeJsonFile):
					updateTreeJsonName(treeJsonFile, nodeId, node.name)		
	return render(request,'createstory/editstory.html',{'nodes':nodes,"story":project})


#TODO Enable login required when the application is launched
#@login_required(login_url='/login')
@csrf_exempt
def StoryBuilder(request,story,node):
	'''
	 Build the XML file of assets and save it on the respective folder
	 of the story.
	 It generates a file system depends on the id of the story where the xml obtained from the flash area is saved.

	'''
	siteUrl = settings.SITE_URL
	#Get the asset file 
	projectModel = Project.objects.get(id = story)
	categories = Category.objects.filter(project__id = story).values('id','name','maxvalue','minvalue')

	#Serialize the queryset categories to JSON to be send top the flash tool.
	reportingJson = json.dumps(list(categories),encoding="utf-8")
	jsonObj = json.loads(reportingJson)
	reportingJson = {"root":jsonObj}
	reportingJson = json.dumps(reportingJson)

	pathLibraries = ""
	for library in projectModel.resourceslibrary.all():
		pathLibraries = pathLibraries + Path(settings.MEDIA_URL).child('assets').child(str(library.id)).child('assets.xml') + "," 
	library = projectModel.resourceslibrary.all()[0]

	##Define all the variables to be sent to the flash application for the node editor
	#assetFile = Path(settings.MEDIA_URL).child('assets').child(str(library.id)).child('assets.xml')
	assetFile = pathLibraries[:-1] #Remove last comma
	nodeFile = Path(settings.MEDIA_ROOT).child('stories').child(str(story)).child('node'+node+'.xml')
	postURL = "/project/story-builder/"+str(story)+"/"+str(node)+"/"
	backUrl = "/project/story/"+str(story)+"/"
	flashFolder = "/static/flash/"
	nodeModel = Node.objects.get(id=node)
	color = projectModel.color_theme
	nextButton = projectModel.next_button
	result={}
	result['status'] = 'fail'
	connectionsNode = []
	#Send true or false depends if it is a end node
	endNode = "false"
	if nodeModel.type == 2: # it is an end node
		endNode = "true"
	tempAttributeNodeList = []
	#Obtain a list of attributes for the node and save them into an array
	attributesTableNode = Attribute.objects.filter(node__id = node,active=True)
	if len(attributesTableNode) > 0:
		for attribute in attributesTableNode:
			tempAttributeNodeList.append(attribute.idAttribute)

	#Obtain the connection of the nodes and save it into an array. It communicates to the flash area the connection
	# in order to warn an user if it disconnects one connection.
	closureTableNode = ClosureTable.objects.filter(node_id__id = node,connected=True)
	if len(closureTableNode) > 0: #Element exist in the table
		for ctNode in closureTableNode:
			connectionsNode.append(ctNode.attribute_id)
	#Using set to get the intersection of the lists
	connectionsNode = list(set(tempAttributeNodeList) & set(connectionsNode))
	connectionsNode = ','.join(connectionsNode)
	'''
	Control the post from the flash tool to save the xml and the options selected
	'''
	if request.method == 'POST':
		if request.POST.get('nodeback'):	
			xmlnode = request.POST['nodeback']
			try:
				xmlnodeFile = ET.fromstring(xmlnode.encode('utf8'))
				#Read the xml sent to get information of the node's options 
				numberOptions = parseXMLNode(xmlnodeFile,nodeModel)
				if numberOptions == 0:					
					nodeModel.options = 1
				else:
					nodeModel.options = numberOptions
				treeObj=ET.ElementTree(xmlnodeFile)
				os.remove(nodeFile)
				with open(nodeFile,'wb+') as f:
					treeObj.write(f)
					f.close()
				nodeModel.xmlFile = nodeFile
				if request.FILES.get('screennode'):
					screenNode= request.FILES['screennode']
					filename, fileExt = os.path.splitext(screenNode.name)
					screenshotPath = Path(settings.MEDIA_ROOT).child('stories').child(str(story)).child('screenshot'+node+fileExt)				
					with open(screenshotPath,"wb+") as screenfile:
						for chunk in screenNode.chunks():
							screenfile.write(chunk)
							screenfile.close()
					nodeModel.imgFile = screenshotPath
				nodeModel.save()
				#if broken == 'true': #If true the tree.json has to be recalculated
				if endNode == "false":
					recalculateTree(node);
			except Exception as e:
				return HttpResponse(str(e))
		else:
			return HttpResponse(str(400))
		return HttpResponse(str(200))
	#The flash application sends the xml file of the node 
	#if request.method == "POST"
	if not os.path.exists(nodeFile):
		file = open(nodeFile,'wb+')#create if the file if it does not exist
		file.close()
	nodeFile = Path(settings.MEDIA_URL).child('stories').child(str(story)).child('node'+node+'.xml')
	nodeModel.xmlFile = nodeFile
	nodeModel.save()
	return render(request,'createstory/storybuilder.html',{"assetFile":assetFile,"nodeFile":nodeFile,
		"SITE_URL":siteUrl,"node":nodeModel,"postURL":postURL,"backUrl":backUrl,"flashFolder":flashFolder,
		"color":color,"nextButton":nextButton, "connectionsNode":connectionsNode, "endNode":endNode, "reportingJson":reportingJson})




#TODO Enable login required when the application is launched
#@login_required(login_url='/login')
@csrf_exempt
def ViewerStory(request,story):
	'''
	This controller handle the preview of the story, it needs to identified the initial node of the story and 
	then move to the next connections depending on the selection of the user. 

	parameter:
		story -> id of the project
	'''
	siteUrl = settings.SITE_URL
	initialNode = Node.objects.get(project__id = story,type=1) #type 1 means initial one
	flashFolder = "/static/flash/"
	postURL = "/project/viewer-story/"+str(story)+"/"
	if request.method == 'POST':
		#Communication through POST with the Flash tool
		result={}
		try:
			if request.POST.get('idnode'):
				nodeId = request.POST['idnode']
				option = request.POST["option"]
				closureTables = ClosureTable.objects.filter(node__id=nodeId,connected = True)
				#Get the option selected and obtain the next node
				if option == "a":
					closureTable = closureTables.filter(attribute_id="a")[0]
				elif option == "b":
					closureTable = closureTables.filter(attribute_id="b")[0]
				elif option == "c":
					closureTable = closureTables.filter(attribute_id="c")[0]
				elif option == "next":
					closureTable = closureTables.filter(attribute_id="n")[0]
				newNode = Node.objects.get(id=closureTable.descendant_id)			
				lastNode = "false"
				if newNode.type == 2:
					lastNode = "true"
				result['xmlNode']=getExtendedPath(newNode.xmlFile.url);
				result['nodeId'] = newNode.id
				result['lastNode'] = lastNode
			elif request.POST.get('storyresult'):
				#Last node sends information about the selections of the node and the time spends to complete the story				
				xmlResults = request.POST['storyresult']
				xmlnodeFile = ET.fromstring(xmlResults.encode('utf8'))
				treeObj=ET.ElementTree(xmlnodeFile)
				tempResultPath = Path(settings.MEDIA_ROOT).child('temp').child('' + str(request.user.id) + "_" + str(story) + ".xml")
				with open(tempResultPath,'wb+') as f:
					treeObj.write(f)
					f.close()
				siteUrl = settings.SITE_URL
				result["url"] = siteUrl + "/project/temp-result/" + story 
				return HttpResponse(json.dumps(result),mimetype="application/json") 
		except Exception as e:
			result["error"] = str(e)
		resultJson = json.dumps(result)
		return HttpResponse(resultJson,mimetype="application/json")
	return render(request,'createstory/viewer.html',{"SITE_URL":siteUrl,"flashFolder":flashFolder,
		"nodeFile":getExtendedPath(initialNode.xmlFile.url),"nodeId":initialNode.id,"postURL":postURL})
			

def ResultTemplate(request, story):
   	'''
   	View to control the temp result 
   	'''   	
	tempResultPath = Path(settings.MEDIA_ROOT).child('temp').child('' + str(request.user.id) + "_" + str(story) + ".xml")
	project = Project.objects.get(id = story)
	if request.method == 'POST':
		if os.path.exists(tempResultPath):
			os.remove(tempResultPath)
		if project.activate == Constants.ACTIVATE_UNPUBLISH:			
			return redirect('admin_edit_story',story = story)
		elif project.activate == Constants.ACTIVATE_PUBLISH:
			return redirect('admin_publish_menu')
	dictCategories = resultTemplate(tempResultPath)
	
	trainersComments = project.reflective
	categories = Category.objects.filter(project__id = project.id)
	return render(request,'unique/trainee_result.html',{"project":project, "reportCategories":dictCategories, "categories": categories, "trainersComments": project.reflective})
