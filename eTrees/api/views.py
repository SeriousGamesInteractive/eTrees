__author__ = 'Felix Rubio (at) SGI'
# Create your views here.
import os
import json
import shutil
from unipath import Path
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from django.http import HttpResponse
from django.conf import settings
from django.core import serializers
from eTrees.utils import returnAdmin
from .utils import sendEmail, updateTreeJson, recalculateTree, deleteContentStory, getExtendedPath
from library.utils import buildXMLAssetFile
from library.models import ResourcesLibrary,GraphicAsset, AudioAsset, AnimationAsset, BackgroundAsset
from account.models import Trainer
from createstory.models import Project, Node, ClosureTable, Attribute, ReportCategory, Category
from publishstory.models import UserGame, ProjectValoration, SessionUser, UserNodeSelection
from uniqueurl.views import generate_url



def requestDeleteAsset(request):
	'''
		API handle the ajax request to delete one asset from the library model.
		The request send the asset id, the asset type and the library id
		Parameter:
			asset_id: asset id,
			asset_type: type of asset( audio,graphic, animation,background)
			lib_id: library id
	'''
	result={}
	result['status'] = 'fail'
	if request.method == 'POST':
		assetId = request.POST['asset_id']
		assetType = request.POST['asset_type']
		libraryId = request.POST['lib_id']
		database = ""
		if assetType == "audio":
			database = AudioAsset.objects.get(id = assetId)
		elif assetType == "graphic":
			database = GraphicAsset.objects.get(id = assetId)
		elif assetType == "animation":
			database = AnimationAsset.objects.get(id = assetId)
		elif assetType == "background":
			database = BackgroundAsset.objects.get(id = assetId)
		#remove the file first and then delete the row in the database
		os.remove(database.pathFile.path)
		database.delete()
		buildXMLAssetFile(libraryId)
		result['status'] = 'ok'
	resultJson = json.dumps(result)
	return HttpResponse(resultJson,mimetype="application/json")



def requestContentAsset(request):
	'''
		API request the content of the asset to show the file in the library.
		Parameter:
			asset_id: asset_id
			asset_type: type of asset( audio,graphic, animation,background)
	'''
	result={}
	result['status'] = 'fail'
	if request.method == 'POST':
		assetId = request.POST['asset_id']
		assetType = request.POST['asset_type']
		database = ""
		if assetType == "audio":
			database = AudioAsset.objects.get(id = assetId)
		elif assetType == "graphic":
			database = GraphicAsset.objects.get(id = assetId)
		elif assetType == "animation":
			database = AnimationAsset.objects.get(id = assetId)
		elif assetType == "background":
			database = BackgroundAsset.objects.get(id = assetId)
		#remove the file first and then delete the row in the database

		result['path'] = getExtendedPath(database.pathFile.path)
		result['name'] = database.name
		result['status'] = 'ok'
	resultJson = json.dumps(result)
	return HttpResponse(resultJson,mimetype="application/json")



def requestDeleteLibrary(request):
	'''
		API request to delete the library from the database.
		The request send as a parameter the library id
		Parameter:
			lib_id: library id
	'''
	result={}
	result['status'] = 'fail'
	

	if request.method == 'POST':
		libId = request.POST['lib_id']
		library = ResourcesLibrary.objects.get(id=libId)
		#Check if the user is admin or the trainer has rights to delete the library
		currentUserId = request.user.id
		isTrainerModel = Trainer.objects.filter(user__id = currentUserId)
		canDelete = False
		if len(isTrainerModel) > 0:
			print "id trainer %d - lib trainer %d" % (isTrainerModel[0].user.id, library.owner_id)
			if isTrainerModel[0].user.id == library.owner_id: #Has rights to delete the library
				canDelete = True
		else:
			canDelete = True

		if canDelete:
			path = Path(settings.MEDIA_ROOT).child('assets').child(str(libId))
			shutil.rmtree(path)
			library.delete()
			result['status'] = 'ok'
		else:
			result['status'] = 'permissions'
			result['message'] = 'You do not have rights to delete the library'
	resultJson = json.dumps(result)
	return HttpResponse(resultJson,mimetype="application/json")


def requestDeleteCategory(request):
	'''
		API remove the category and check all the xml files created to remove the category from them
	'''
	result = {}
	result["status"] = 'fail'
	if request.method == 'POST':
		try:
			projectId = request.POST['projectid']
			categoryId = request.POST['categoryid']
			folderpath = Path(settings.MEDIA_ROOT).child('stories').child(str(projectId))

			category = Category.objects.get(id = categoryId)

			nodes = Node.objects.filter(project__id = projectId)
			for node in nodes:
				#Delete the report category related with the category to delete
				for attribute in Attribute.objects.filter(node__id = node.id):
					reportCategories = ReportCategory.objects.filter(attribute__id = attribute.id, name = category.name)
					for reportCategory in reportCategories:
						reportCategory.delete()
				#Delete the category in the xml file
				nodeXMLFile = folderpath.child('node'+str(node.id)+'.xml')
				tree = ET.parse(nodeXMLFile)
				root = tree.getroot()
				#Find the element and change the name
				for report in root.iter('reporting'):
					for child in report:
						if child.attrib['name'] == category.name:
							report.remove(child)
							break
				tree.write(nodeXMLFile)
			category.delete() #Remove the category itself
			result["status"] = 'ok'
			resultJson = json.dumps(result)
			return HttpResponse(resultJson,mimetype="application/json")
		except Exception as e:
			result['error'] = str(e)
	resultJson = json.dumps(result)
	return HttpResponse(resultJson,mimetype="application/json")


def requestDeleteNode(request):
	'''
		API remove the node requested. It also removes the connections and the xml file created for that node.
	'''
	result={}
	result['status'] = 'fail'
	if request.method == 'POST':
		try:
			nodeId = request.POST['nodeid']
			storyId = request.POST['storyid']

			projectModel = Project.objects.get(id = storyId)

			#Check if the user is admin or the trainer has rights to delete the library
			currentUserId = request.user.id
			isTrainerModel = Trainer.objects.filter(user__id = currentUserId)
			canDelete = False
			if len(isTrainerModel) > 0:
				if isTrainerModel[0].user.id == projectModel.owner_id: #Has rights to delete the library
					canDelete = True
			else:
				canDelete = True

			if canDelete:
				node = Node.objects.get(id=nodeId)
				initialNode = node.type
				attributeTables = Attribute.objects.filter(node__id = nodeId)
				for attributeTable in attributeTables:
					reportCategory = ReportCategory.objects.filter(attribute__id = attributeTable.id)
					if reportCategory:
						reportCategory.delete()	
					attributeTable.delete()
				recalculateTree(nodeId,True) #Delete the node from the connection tree file (JSON)		
				node.delete()
				#Check if the tree.json file exist and then remove the ClosureTable
				nodeXml =Path(settings.MEDIA_ROOT).child('stories').child(str(storyId)).child("node"+nodeId+".xml")
				jsonFile = Path(settings.MEDIA_ROOT).child('stories').child(str(storyId)).child('tree.json')
				screenshootFile = Path(settings.MEDIA_ROOT).child('stories').child(str(storyId)).child("screenshot"+nodeId+".jpg")
				#Remove the Attribute table of the node

				if os.path.exists(jsonFile):
					closureTable = ClosureTable.objects.filter(node__id = nodeId)
					if len(closureTable) > 0:
						closureTable[0].delete();
					#os.remove(jsonFile)
				if os.path.exists(nodeXml):
					os.remove(nodeXml)
				if os.path.exists(screenshootFile):
					os.remove(screenshootFile)
				result['status'] = 'ok'
				result['initial_node'] = initialNode
			else:
				result['status'] = 'permissions'
				result['message'] = 'You do not have rights to delete this node'
		except Exception as e:
			result['error'] = str(e)
	resultJson = json.dumps(result)
	return HttpResponse(resultJson,mimetype="application/json")


def requestCopyNode(request):
	'''
		API request to copy the node.
		Receive the id of the node to copy and generate a duplication of the node inside the same project.
	'''
	result={}
	result['status'] = 'fail'
	print "Has arrived"
	if request.method == 'POST':
		try:
			nodeId = request.POST['nodeid']
			storyId = request.POST['storyid']
			nameNode = request.POST['namenode']
			#Check if the name already exists
			checkName = Node.objects.filter(project__id = storyId, name = nameNode).count()
			if checkName > 0:
				result["error"] = "The name of the node already exists in this story."
				resultJson = json.dumps(result)
				return HttpResponse(resultJson,mimetype="application/json")
			projectModel = Project.objects.get(id = storyId)
			node = Node.objects.get(id=nodeId)

			#Get the data of the node into the new Class dNode
			nodeType = node.type
			dNode = Node()
			nodeXMLFile = Path(settings.MEDIA_ROOT).child('stories').child(str(node.project.id)).child('node'+str(node.id)+'.xml')
			nodeImageFile = node.imgFile	
			dNode.name = nameNode
			dNode.description = node.description
			dNode.type = node.type
			dNode.project = projectModel
			dNode.options = node.options					
			dNode.save()
			#Get the path of the duplication xml for the node
			duplicateXmlFile = Path(settings.MEDIA_ROOT).child('stories').child(str(node.project.id)).child('node'+str(dNode.id)+'.xml')
			shutil.copyfile(nodeXMLFile,duplicateXmlFile)					
			dNode.xmlFile = duplicateXmlFile
			duplicateImageNodeFile = Path(settings.MEDIA_ROOT).child('stories').child(str(projectModel.id)).child('screenshot'+str(dNode.id)+'.jpg')
			try:								
				#Make a copy of the node's screenshot
				with open(duplicateImageNodeFile,'wb+'):
					shutil.copyfile(nodeImageFile,duplicateImageNodeFile)					
				
			except IOError as e:
				result["error"] = str(e)
				resultJson = json.dumps(result)
				return HttpResponse(resultJson,mimetype="application/json")
				print "Screenshoot %d does not exist" % (dNode.id)

			attributesNodes = Attribute.objects.filter(node__id=node.id, active= True)
			#Duplicate the attributes 
			for attribute in attributesNodes:
				dAttributeNode = Attribute()			
				dAttributeNode.node = dNode
				dAttributeNode.idAttribute = attribute.idAttribute
				dAttributeNode.active = True				
				dAttributeNode.save()
				#Duplite report category
				reportCategories = ReportCategory.objects.filter(attribute__id = attribute.id)
				for reportCategory in reportCategories:
					dReportCategory = ReportCategory()
					dReportCategory.value = reportCategory.value
					dReportCategory.name = reportCategory.name
					dReportCategory.attribute = dAttributeNode
					dReportCategory.save()
			result['initial_node'] = nodeType

			dNode.save()
			result['status'] = 'ok';
		except Exception as e:
			result['error'] = str(e)
	resultJson = json.dumps(result)
	return HttpResponse(resultJson,mimetype="application/json")

def requestSaveTree(request):
	'''
		API request to save the tree.
		Send the json with all the information of the tree and this file has to be saved related with the project.
		Parameter:
			tree_json: json file with the content of the canvas
			project_id: project id to relate the tree with the project
	'''
	result={}
	result['status'] = 'fail'
	if request.method == 'POST':
		data = request.POST['json_tree']
		projectId = request.POST['project_id']
		jsonFile = Path(settings.MEDIA_ROOT).child('stories').child(str(projectId)).child('tree.json')
		with open(jsonFile,'wb') as f:
			json.dump(data,f)
		result['status'] = 'ok'
	resultJson = json.dumps(result)
	return HttpResponse(resultJson,mimetype="application/json")



def requestLoadTree(request):
	'''
		API to request the json file save in the connection tree proccess.
		Parameter:
			project_id: Id of the project
	'''
	result={}
	result['status'] = 'fail'
	if request.method == 'POST':
		projectId = request.POST['project_id']
		jsonFile= Path(settings.MEDIA_ROOT).child('stories').child(str(projectId)).child('tree.json')
		if os.path.exists(jsonFile):

			try:
				json_data = open(jsonFile)
				data = json.load(json_data)
				result['json'] = data
				result['status'] = 'ok'
			except:
				pass
	resultJson = json.dumps(result)
	return HttpResponse(resultJson,mimetype="application/json")



def requestNodeData(request):
	'''
		API request the data for each of the node sent
		Parameter:
			nodes:array of the ids for the nodes.
	'''

	result = {}
	result['status'] = 'fail'
	result['nodes'] =[]
	print request.POST
	if request.method == 'POST':
		try:
			for node in request.POST.getlist('nodes[]'):
				print node
				nodeFetch ={}
				nodeModel = Node.objects.get(id=node)
				nodeFetch['id'] = nodeModel.id
				nodeFetch['name'] = nodeModel.name
				nodeFetch['type'] = nodeModel.type
				nodeFetch['description'] = nodeModel.description
				nodeFetch['options'] = nodeModel.options
				nodeFetch['imgFile'] = nodeModel.imgFile
				attribModels = Attribute.objects.filter(node__id = node,active = True).order_by('idAttribute')
				nodeFetch['attributes'] = [] #If there is not attributes "n" means next attribute is up
				for attribModel in attribModels:
					nodeFetch['attributes'].append({"attributeId": attribModel.idAttribute})
				result['nodes'].append(nodeFetch)
			result['status']='ok'
				
		except Exception as e:
			result['error'] = str(e)
			return HttpResponse(json.dumps(result),mimetype="application/json")
	return 	HttpResponse(json.dumps(result),mimetype="application/json")



def requestSearchNode(request):
	'''
		API request the search of the node base on its name.
		Parameter:
			search: the text introduce in the input text.
	'''
	result = {}
	result['status'] = 'fail'
	if request.method == 'POST':
		searchText= request.POST['search']			
		projectId = request.POST['projectId']
		nodes = Node.objects.filter(project__id =projectId,name__istartswith=searchText)
		result['status'] = 'ok'
		result['nodes'] = serializers.serialize('json',nodes,fields=('name','type','id'))
	resultJson = json.dumps(result)
	return HttpResponse(resultJson,mimetype="application/json")



def requestPublishProject(request):
	'''
		API to create the make clone of the project table and the nodes in order to publish 
		the story
	'''
	result = {}
	result['status'] = 'fail'
	relationNodePNode = {} # relation between nodes and publish nodes
	relationCategoryPCategory = {} #relation between the category and the publish category
	if request.method == 'POST':
		try:
			'''
				This is a duplication of the story to publish it and not modify the story in the unpublish section
				1- Duplication of the project (story)
				2- Duplication of all the nodes contained in the story
				3- Duplication of the connection of these nodes with the ClosureTable
			'''

			projectid = request.POST['projectId']
			namePublishStory = request.POST['nameStory']
			#check if the name already exist
			adminUser = returnAdmin(request.user)
			checkNameProject = Project.objects.filter(name = namePublishStory, user__id = adminUser.id, activate=1).count()
			if checkNameProject > 0:
				result['error'] = "The name of the story already exist"
				return HttpResponse(json.dumps(result),mimetype="application/json")
			#Check if exist an initial node in the story	
			if Node.objects.filter(project__id = projectid,type=1).count() < 1:
				result['error'] = "You must create an initial node to publish the story."
				return HttpResponse(json.dumps(result),mimetype="application/json")
			#Check if the connection tree file exists
			treeJson = Path(settings.MEDIA_ROOT).child('stories').child(str(projectid)).child('tree.json')
			if not os.path.isfile(treeJson):
				result['error'] = "You must create the connections between nodes to publish the story"
				return HttpResponse(json.dumps(result),mimetype="application/json")
			############################		
			project = Project.objects.get(id=projectid)
			pProject = Project()
			if project.canPublish:
				pProject.name = namePublishStory
				pProject.topic = project.topic
				pProject.description = project.description
				pProject.reflective = project.reflective
				pProject.color_theme = project.color_theme
				pProject.activate = 1
				pProject.owner_id = project.owner_id
				pProject.save()

				for library in project.resourceslibrary.all():
					pProject.resourceslibrary.add(library)
				#Categories
				categories = Category.objects.filter(project__id = project.id)
				for category in categories:
					pCategory = Category();
					pCategory.maxvalue = category.maxvalue
					pCategory.minvalue = category.minvalue
					pCategory.name = category.name
					pCategory.description = category.description
					pCategory.project = pProject
					pCategory.save() 
					relationCategoryPCategory[category.id] = pCategory.id

				#Create the folder for the duplication of the project to save all the files required
				folderpath = Path(settings.MEDIA_ROOT).child('publish').child(str(pProject.id))	
				if not os.path.exists(folderpath): 
					os.makedirs(folderpath)

				for user in project.user.all():
					pProject.user.add(user)
				nodes = Node.objects.filter(project__id__exact = project.id)
				'''
					Duplicate the content of the node database when the story is published
						- Duplicate also the xml file and the image file.
				'''
				for node in nodes:
					pNode = Node()
					nodeXMLFile = Path(settings.MEDIA_ROOT).child('stories').child(str(node.project.id)).child('node'+str(node.id)+'.xml')
					nodeImageFile = node.imgFile	
					pNode.name = node.name
					pNode.description = node.description
					pNode.type = node.type
					pNode.project = pProject
					pNode.options = node.options					
					pNode.save()
					publishNodeXMLFile = Path(settings.MEDIA_ROOT).child('publish').child(str(pProject.id)).child('node'+str(pNode.id)+'.xml')
					shutil.copyfile(nodeXMLFile,publishNodeXMLFile)					
					pNode.xmlFile = publishNodeXMLFile
					publishImageNodeFile = Path(settings.MEDIA_ROOT).child('publish').child(str(pProject.id)).child('screenshot'+str(pNode.id)+'.jpg')
					
					try:
						with open(publishImageNodeFile, 'wb+'):
							shutil.copyfile(nodeImageFile,publishImageNodeFile)
					except IOError as e:
						print "Screenshoot %d does not exist" % (pNode.id)
												
					pNode.save()
					relationNodePNode[node.id]=pNode.id
				#Duplicate tree json file for the publish story and modify the id nodes 

				treeJson = Path(settings.MEDIA_ROOT).child('stories').child(str(project.id)).child('tree.json')
				publishTreeJson = Path(settings.MEDIA_ROOT).child('publish').child(str(pProject.id)).child('tree.json')
				shutil.copyfile(treeJson,publishTreeJson)
				updateTreeJson(publishTreeJson,relationNodePNode)
				closureNodes = ClosureTable.objects.filter(node__project__id__exact=project.id)

				for cnode in closureNodes:			
					pClosureNode =  ClosureTable()
					pNode = Node.objects.get(id=relationNodePNode[cnode.node.id])
					pClosureNode.node = pNode
					if not cnode.descendant_id:
						pClosureNode.descendant_id = 0
					else:
						pClosureNode.descendant_id = relationNodePNode[cnode.descendant_id]
					pClosureNode.attribute_id = cnode.attribute_id
					pClosureNode.connected = cnode.connected
					pClosureNode.save()
				#Duplicate the attribute table for the publish story
				attributesNodes = Attribute.objects.filter(node__project__id__exact=project.id)
				for cattribute in attributesNodes:			
					pAttributeNode =  Attribute()
					pNode = Node.objects.get(id=relationNodePNode[cattribute.node.id])
					pAttributeNode.node = pNode
					pAttributeNode.idAttribute = cattribute.idAttribute					
					pAttributeNode.active = cattribute.active					
					pAttributeNode.save()
					#Duplite report category
					reportCategories = ReportCategory.objects.filter(attribute__id = cattribute.id)
					for reportCategory in reportCategories:
						pReportCategory = ReportCategory()
						pReportCategory.name = reportCategory.name
						pReportCategory.value = reportCategory.value
						pReportCategory.attribute = pAttributeNode
						pReportCategory.save()
				result['status'] = 'ok'
			else:
				result['error'] = 'Need to finish the creation of the story.'
		except Exception as e:
			result['error'] = str(e)
			print "ERROR ", e
			return HttpResponse(json.dumps(result),mimetype="application/json")
		
		return 	HttpResponse(json.dumps(result),mimetype="application/json")

def requestRemoveUserStory(request):
	'''
		API include an user into the story
		Send the email with the invitation for the users.
		Parameter:
			idstory: the id of the story
			users: array id of the user to add
	'''
	result = {}
	result['status'] = 'fail'
	if request.method == 'POST':
		try:
			idStory = request.POST["idstory"]
			story = Project.objects.get(id= idStory)
			result['storyname'] = story.name
			for userId in request.POST.getlist("userIDs"):
				userModel = UserGame.objects.get(id = userId)
				projectValoration = ProjectValoration.objects.get(project__id = story.id, user__id=userModel.id)
				
				projectValoration.active = False
				projectValoration.save()
				
			result['status'] = 'ok'
		except Exception as e:
			result['error'] = str(e)
			return HttpResponse(json.dumps(result),mimetype="application/json")
	return 	HttpResponse(json.dumps(result),mimetype="application/json")
	
def requestAddUserStory(request):	
	'''
		API include an user into the story
		Send the email with the invitation for the users.
		Parameter:
			idstory: the id of the story
			users: array id of the user to add
	'''
	result = {}
	result['status'] = 'fail'
	result['users_used'] = []	
	result['users_added']= []
	result['users_added_counter'] = 0
	if request.method == 'POST':
		try:
			idStory = request.POST["idstory"]
			story = Project.objects.get(id= idStory)
			result['storyname'] = story.name
			extraMessage = request.POST['extraMessage']			
			for userId in request.POST.getlist("users"):
				userModel = UserGame.objects.get(id = userId)
				projectValoration = ProjectValoration.objects.filter(project__id = story.id, user__id=userModel.id)
				if len(projectValoration) < 1: #The user can be included to the story													
					newProjectValoration = ProjectValoration(user=userModel,project=story,completed=False)
					result['users_added'].append({"name":userModel.name,"surname":userModel.surname,"username":userModel.username,"id":userModel.id})
					result['users_added_counter'] +=1
					newProjectValoration.save()					
					uniqueUrlObj = generate_url(newProjectValoration)
					#Link to start the story
					url = settings.SITE_URL + "/game/"+ uniqueUrlObj.url					
					returnEmail = sendEmail(userModel.email,url, userModel.name, story.name, extraMessage) 
					if returnEmail != "success":					
						raise Exception(returnEmail)
				else:
					newProjectValoration = ProjectValoration.objects.get(project__id = story.id, user__id=userModel.id)
					
					if newProjectValoration.active == False:
						newProjectValoration.active = True
						newProjectValoration.save()
												
						result['users_added'].append({"name":userModel.name,"surname":userModel.surname,"username":userModel.username,"id":userModel.id})
						result['users_added_counter'] +=1
						
						uniqueUrlObj = generate_url(newProjectValoration)
						#Link to start the story
						url = settings.SITE_URL + "/game/"+ uniqueUrlObj.url					
						returnEmail = sendEmail(userModel.email,url, userModel.name, story.name, extraMessage) 
						if returnEmail != "success":					
							raise Exception(returnEmail)
					else:
						result['users_used'].append(userId)
			result['status'] = 'ok'
		except Exception as e:
			result['error'] = str(e)
			return HttpResponse(json.dumps(result),mimetype="application/json")
	return 	HttpResponse(json.dumps(result),mimetype="application/json")



def requestUsersOnStories(request):
	'''
		API return the number of users invitated to the story
		Parameter:
			idstory: the id of the story
			
	'''
	result = {}
	result['status'] = 'fail'
	result['stories'] =[]
	#Output {"stories"[{"storyId":x,users:[{"name":xxx,"surnama":xxxx,"username":xxxx,"id":xxxx}]}]}
	if request.method == 'POST':
		try:
			for storyId in request.POST.getlist('stories'):
				projectsValoration = ProjectValoration.objects.filter(project__id = storyId)
				project = Project.objects.get(id=storyId)
				users = []
				
				for projectValoration in projectsValoration:
					if projectValoration.active:
						users.append({"name":projectValoration.user.name,"surname":projectValoration.user.surname,
							"username":projectValoration.user.username,"id":projectValoration.user.id});
							
				result['stories'].append({"storyid":storyId,"storyname":project.name,"users":users})
			result['status']='ok'
		except Exception as e:
			result['error'] = str(e)
			return HttpResponse(json.dumps(result),mimetype="application/json")
	return 	HttpResponse(json.dumps(result),mimetype="application/json")




def requestUserInviteStory(request):
	'''
		API request the users invited to the story
		Parameter:
			idstory: the id of the story
			
	'''
	result = {}
	result['status'] = 'fail'

	if request.method == 'POST':
		try:
			storyid = request.POST['storyid']
			projectsValoration = ProjectValoration.objects.filter(project__id = storyid)
			result['storyname'] = projectsValoration[0].project.name
			result['users'] = []
			for projectValoration in projectsValoration:
				result['users'].append({"name":projectValoration.user.name,"surname":projectValoration.user.surname})
			result['status']='ok'
		except Exception as e:
			result['error'] = str(e)
			return HttpResponse(json.dumps(result),mimetype="application/json")
	return HttpResponse(json.dumps(result),mimetype="application/json")

'''
PUBLISH 
'''

def requestDeletePublishStory(request):
	'''
	Remove the publish story if there is not user assigned and if the user has the enought rights to do it.
	'''
	result={}
	result['status'] = 'fail'
	if request.method == 'POST':
		try:
			storyId = request.POST['storyid']
			print "The id of the story is: ",storyId
			projectModel = Project.objects.get(id = storyId)
			#Check if the user is admin or the trainer has rights to delete the library
			currentUserId = request.user.id
			isTrainerModel = Trainer.objects.filter(user__id = currentUserId)
			canDelete = False
			if len(isTrainerModel) > 0:
				if isTrainerModel[0].user.id == projectModel.owner_id: #Has rights to delete the library
					canDelete = True
			else:
				canDelete = True
			if canDelete:

				#Deactivate the project so it cannot be seen for the administration or the trainee
				projectModel.deactivatePublish()
				
				##Implementation to delete the content of a published story
				# projectValoration = ProjectValoration.objects.filter(project__id = storyId).count()
				# if projectValoration > 0: # It cannot be remove because there is users assigned to the story
				# 	result["error"] = 'The story cannot be removed, users already invited'
				# 	resultJson = json.dumps(result)
				# 	return HttpResponse(resultJson,mimetype="application/json")
				# deleteContentStory(projectModel,'publish')
				# categories = Category.objects.filter(project__id = projectModel.id)
				# categories.delete()
				# projectModel.delete()
				result['status'] = 'ok'
			else:
				result['status'] = 'permissions'
				result['message'] = 'You do not have rights to delete this node'
		except Exception as e:
			result['error'] = str(e)
	resultJson = json.dumps(result)
	return HttpResponse(resultJson,mimetype="application/json")

'''
	REPORTING REQUEST 
'''

def requestCompleteStoryUsers(request):
	'''
		API request the users who complete the story
		Parameter:
			story_id: the id of the story
	'''
	result = {}
	result['status'] = 'fail'

	if request.method == 'POST':
		try:
			
			storyid = request.POST['storyid']
			projectsValoration = ProjectValoration.objects.filter(project__id = storyid,completed=True)
			categories = Category.objects.filter(project__id = storyid).values("name","maxvalue","minvalue")
			result["users"] = []
			for projectVal in projectsValoration:
				tempSession = SessionUser.objects.filter(projectValoration__id = projectVal.id).order_by('startTime').values('id','rating')
				result["users"].append({'id':projectVal.id,'name':projectVal.user.name, 'categories':list(categories),
				 'username':projectVal.user.username,'sessions':list(tempSession)})			
				result["story_name"] = projectVal.project.name

			result['status']='ok'
		except Exception as e:
			result['error'] = str(e)
			return HttpResponse(json.dumps(result),mimetype="application/json")
	return HttpResponse(json.dumps(result),mimetype="application/json")


def requestSessionGameUsers(request):
	'''
		API request the information of the game for the session requested
		Parameter:
			sessionId: session of the game played
	'''
	result = {}
	result['status'] = 'fail'

	if request.method == 'POST':
		try:			
			sessionId = request.POST['sessionId']
			sessionModel = SessionUser.objects.get(id = sessionId)
			#It needs to send the information of the questions answer, the value of the attributes
			nodesSelected = UserNodeSelection.objects.filter(sessionUser__id = sessionModel.id)
			result["session"] = []
			result["categories"] = []
			for nodeSelect in nodesSelected:
				if nodeSelect.attributeSelected != "end" and nodeSelect.attributeSelected != "next":
					#Calculate average maximum minimum
					attributes = Attribute.objects.filter(node__id = nodeSelect.node.id, active=True)	
					dictCategories = {}
					for attribute in attributes:
						reportCategories = ReportCategory.objects.filter(attribute__id = attribute.id)						
						for reportCategory in reportCategories:
							dictCategories.setdefault(reportCategory.name,[0]).append(reportCategory.value)	
							'''						
							try:
								dictCategories[reportCategory.name].append(reportCategory.value)
							except:
								dictCategories[reportCategory.name] = [0]#Include 0 to make at least 0 the minimum value
								dictCategories[reportCategory.name].append(reportCategory.value)
							'''
					#From the dict create with the value of the categories, it is obtained the max and min value
					print "DCatego: ",dictCategories
					categoryRange = []
					for key in dictCategories:
						categoryRange.append({"name":key,"maxvalue":max(dictCategories[key]),"minvalue":min(dictCategories[key])})

					attributeSelected = Attribute.objects.get(node__id = nodeSelect.node.id, idAttribute = nodeSelect.attributeSelected)
					listCategories = []
					if attributeSelected:
						reportCategories = ReportCategory.objects.filter(attribute__id = attributeSelected.id).values('name','value')
						result["session"].append({"node_id":nodeSelect.node.id,"node_name":nodeSelect.node.name,"option_name":attributeSelected.idAttribute,
							"categories":list(reportCategories),"categoryRange":categoryRange})

				else:
					result["session"].append({"node_id":nodeSelect.node.id,"node_name":nodeSelect.node.name,"option_name":nodeSelect.attributeSelected,
							"categories":[],"maxvalue":None,"minvalue":None})

			projectCategory = Category.objects.filter(project__id = sessionModel.projectValoration.project.id).values('name','maxvalue','minvalue')
			#result['categories'] = list(projectCategory)
			result['status']='ok'
		except Exception as e:
			result['error'] = str(e)
			return HttpResponse(json.dumps(result),mimetype="application/json")
	return HttpResponse(json.dumps(result),mimetype="application/json")


	
