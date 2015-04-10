
import os
import shutil
import json
import sys
from unipath import Path
from django.conf import settings
from eTrees.global_constants import Constants
from account.models import Trainer
from library.models import ResourcesLibrary
from .models import Project, Node, ClosureTable, Attribute, ReportCategory, Category
from api.utils import updateTreeJson
try:
	import xml.etree.cElementTree as ET
except ImportError:
	import xml.etree.ElementTree as ET


def parseXMLNode(xmlnode,node):
	''''
	Read the xml to obtain the options selected in the flash ( storybuilder tool).
	The options are saved in the database in the table attributes, connected to node table.
	'''
	counterOption = 0
	options = None
	
	for child in xmlnode:
		if child.tag == "options":
			options = child
	#Check if options are included in the xml
	if options:
		#Obtain the table attributes otherwise, generate one.
		attributes = Attribute.objects.filter(node__id = node.id)
		for attribute in attributes:
			attribute.active = False
			attribute.save()
		for option in options:
			if option.attrib['status'] == "true":
				counterOption = counterOption + 1
				attribute = Attribute.objects.filter(node__id = node.id, idAttribute = option.attrib['option'])
				if len(attribute) < 1:
					attribute = Attribute()
				else:
					attribute = attribute[0]
				attribute.idAttribute = option.attrib['option']
				attribute.active = True
				attribute.node = node							
				attribute.save()
				defaultCategories = Category.objects.filter(project__id = node.project.id)

				#Initialize the report categories from the category table created in the creation of the story
				for category in defaultCategories: #todo - check if defaultCategories is right
					existCategory = ReportCategory.objects.filter(attribute__id =attribute.id, name = category.name).count()
					if existCategory == 0:
						reportModel = ReportCategory(attribute=attribute,name = category.name,value = 0)
						reportModel.save()
				#Include the value selected for the category in the edtion of the node and save it on the table reportCategory
				for parameter in option.findall('./reporting/item'):
					category = Category.objects.get(project__id = node.project.id, name = parameter.attrib['name'])
					reportModel = ReportCategory.objects.filter(attribute__id =attribute.id, name = parameter.attrib['name'])
					if len(reportModel) > 0:
						reportModel = reportModel[0]
						reportModel.value = parameter.text
					else:
						reportModel = ReportCategory(attribute=attribute, name=category.name, value=parameter.text)
					reportModel.save()
	#Return the number of options available for the node
	return counterOption

def deleteContentStory(project):
	'''
	NOT LONGER IN USE - The story gets delete by changing the type of story
	Delete all the content save it on the folder

	'''    
	folderpath = Path(settings.MEDIA_ROOT).child('stories').child(str(project.id))
	shutil.rmtree(folderpath)

	nodes = Node.objects.filter(project__id = project.id)
	for node in nodes:
		attributeTables = Attribute.objects.filter(node__id = node.id)
		for attributeTable in attributeTables:
			reportCategory = ReportCategory.objects.filter(attribute__id = attributeTable.id)
			if reportCategory:
				reportCategory.delete()	
			attributeTable.delete()	
		closuresTables = ClosureTable.objects.filter(node__id = node.id)
		if len(closuresTables)> 0:
			for closuretable in closuresTables:
				closuretable.delete()	
		node.delete()
		
	
def copyStory(project, newProject, relationCategoryNCategory):
	'''
		Generate the duplication of the values on the database tables from one story and also the files system generated for it.

	'''
	try:
		#Add the libraries of the project to be copied
		for library in project.resourceslibrary.all():
			newProject.resourceslibrary.add(library)

		relationNodePNode = {} # relation between nodes

		#Create the folder for the duplication of the project to save all the files required
		folderpath = Path(settings.MEDIA_ROOT).child('stories').child(str(newProject.id))	
		if not os.path.exists(folderpath): 
			os.makedirs(folderpath)

		for user in project.user.all():
			newProject.user.add(user)
		nodes = Node.objects.filter(project__id__exact = project.id)
		'''
			Duplicate the content of the node database
			- Duplicate also the xml files and the image files.
		'''
		for node in nodes:
			pNode = Node()
			nodeXMLFile = Path(settings.MEDIA_ROOT).child('stories').child(str(node.project.id)).child('node'+str(node.id)+'.xml')
			pNode.name = node.name
			pNode.description = node.description
			pNode.type = node.type
			pNode.project = newProject
			pNode.options = node.options					
			pNode.save()
			newNodeXMLFile = Path(settings.MEDIA_ROOT).child('stories').child(str(newProject.id)).child('node'+str(pNode.id)+'.xml')			
			shutil.copyfile(nodeXMLFile,newNodeXMLFile)								
			pNode.xmlFile = newNodeXMLFile
			newImageNodeFile = Path(settings.MEDIA_ROOT).child('stories').child(str(newProject.id)).child('screenshot'+str(pNode.id)+'.jpg')
			imageNodeFile = Path(settings.MEDIA_ROOT).child('stories').child(str(project.id)).child('screenshot'+str(node.id)+'.jpg')
			try:
				shutil.copyfile(imageNodeFile,newImageNodeFile)
			except Exception as e:
				print "Error ", str(e)
			pNode.imgFile = newImageNodeFile
			pNode.save()
			relationNodePNode[node.id]=pNode.id
		#Modify the category in the xml if the name of the category has changed
		if len(relationCategoryNCategory) > 0:
			categories = Category.objects.filter(project__id = project.id)
			for category in categories:
				if category.id in relationCategoryNCategory:
					newCategoryName =relationCategoryNCategory[str(category.id)]['name'] #Obtaine name new category
					editNameCategory(newProject,category.name, newCategoryName)

		#Duplicate tree json file for the publish story and modify the id nodes 
		treeJson = Path(settings.MEDIA_ROOT).child('stories').child(str(project.id)).child('tree.json')
		newTreeJson = Path(settings.MEDIA_ROOT).child('stories').child(str(newProject.id)).child('tree.json')
		if os.path.isfile(treeJson):
			shutil.copyfile(treeJson,newTreeJson)
			updateTreeJson(newTreeJson,relationNodePNode)
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
				#Include the modification of the category name to the reportCategory
				category = Category.objects.filter(project__id = project.id, name = reportCategory.name)
				if len(category) > 0:
					category = category[0]
					pReportCategory.name = relationCategoryNCategory[str(category.id)]['name']
					pReportCategory.value = reportCategory.value
					pReportCategory.attribute = pAttributeNode
					pReportCategory.save()
		return True
	except Exception as e:

		return str(e)

def validateCreateEditStoryForm(request, trainerUser, project = None, categories = [], copyFlag = False):
	'''
	 This method handles the creation, copy and edition of a story by obtaining the value through the request.
	 parameter
	 	request
	 	trainerUser -> user who owns the story
	 	project (optional) -> if it is not None, means the project could be edited or copyStory
	 	categories (optional) -> list of categories that a project contains already
	 	copyFlag (optional) -> indicated if the story has to be copied
	'''
	try:
		if not bool(request.POST.get('name',False)):
			return {'status':'error', 'message':"You need to give a name to the story"}
		if not bool(request.POST.get('topic',False)):
			return {'status':'error', 'message':"You need to write the topic for the story"}
		if (not bool(request.POST.get('select-library',False))) and project == None and copyFlag == False:
			return {'status':'error', 'message':"You need to select a library for the story"}

		#Check categories
		listNameCategories = []
		#Loop the categories through the new categories addedand check the names, saving them on an array called listNameCategories
		for i in range(len(categories),int(request.POST['numberCategories'])):
			if not bool(request.POST.get('nameCategory'+str(i),False)):
				return {'status':'error','message':"You need to give a name to the category added"}
			listNameCategories.append(request.POST.get('nameCategory'+str(i)).lower())

		#Loop through the categories already added to the story and include them into the listNameCategories
		#then it checks the names on the categories to warn the user for the duplication.
		for category in categories:
			listNameCategories.append(request.POST.get("name-"+ str(category.id)))
			if not bool(request.POST.get("name-"+ str(category.id),False)):
				return {'status':'error', 'message':"You need to give a name to the category added"}
		if len(listNameCategories) != len(set(listNameCategories)): #Exist duplicate name in the categories
			return {'status':'error', 'message':"You cannot use the same name for two or more categories."}
		#Get the data from the request.POST and save it in the story table.	
		storyName = request.POST['name']
		checkStoryName = Project.objects.filter(user__id = request.user.id, name=storyName, activate = Constants.ACTIVATE_UNPUBLISH)
		if len(checkStoryName)> 0 and project == None: #story name already exist, it is not allowed
			return {'status':'error', 'message':"The name of the story already exist"}
		storyTopic = request.POST['topic']
		storyDescription = request.POST['description']
		storyReflective = request.POST['reflective']
		colorTheme = request.POST['colorpicker']
		nextButton = request.POST['next-button']

		oldProject = None#Declare this variable in case it is a copy of the story
		if project == None:
			#This case a new story is created
			project = Project(name=storyName,topic=storyTopic,description=storyDescription,
				reflective=storyReflective,activate=0,color_theme = colorTheme,owner_id = request.user.id, next_button = nextButton)
			project.save()
			project.user.add(request.user)
			#If the current use is a trainer, then we give access to the story to the admin
			if len(trainerUser)>0: # if true, the user is a trainer not admin
				adminModel = trainerUser[0].admin		
				project.user.add(adminModel)
		elif copyFlag:
			#A story is copied
			oldProject = project #save the project parameter into the variable oldProject
			project = Project(name=storyName,topic=storyTopic,description=storyDescription,
				reflective=storyReflective,activate=0,color_theme = colorTheme,owner_id = request.user.id, next_button = nextButton)
			project.save()
			project.user.add(request.user)
			#If the current use is a trainer, then we give access to the story to the admin
			if len(trainerUser)>0: # if true, the user is a trainer not admin
				adminModel = trainerUser[0].admin		
				project.user.add(adminModel)
		else:	
			#A story is edited
			project.name = storyName
			project.topic = storyTopic
			project.description = storyDescription
			project.reflective = storyReflective
			project.color_theme = colorTheme
			project.next_button = nextButton
			project.save()
		#Give access to the library to the trainers selected
		for library in request.POST.getlist('select-library'):
			libraryModel = ResourcesLibrary.objects.get(id=library)
			project.resourceslibrary.add(libraryModel)
			#Increase flag of libraries used
			libraryModel.inUse = libraryModel.inUse + 1
			libraryModel.save()
		
		postUsers = request.POST.getlist('trainers')
		postTrainers = Trainer.objects.filter(id__in=postUsers)
		postTrainersUserIDs = list()
		
		for postTrainer in postTrainers:
			postTrainersUserIDs.append(postTrainer.user.id)
		
		for projectUser in project.user.exclude(id__in=postTrainersUserIDs):
			if Trainer.objects.filter(id=projectUser.id).count() > 0 and projectUser.id != project.owner_id:
				project.user.remove(projectUser)
		
		#Give access to the story to the trainers selected
		for trainer in postUsers:
			project.user.add(Trainer.objects.get(id=trainer).user)
		
		#Create story folder	
		folderpath = Path(settings.MEDIA_ROOT).child('stories').child(str(project.id))	
		if not os.path.exists(folderpath): 
			os.makedirs(folderpath)

		#Save the new categories in the database table Category, obtaining the information from the request.POST['numberCategories']
		for i in range(len(categories),int(request.POST['numberCategories'])):
			nameCategory = request.POST['nameCategory'+str(i)]
			minvalue = request.POST['minvalue'+str(i)]
			maxvalue = request.POST['maxvalue'+str(i)]
			descriptionCat = request.POST['descriptionCategory'+str(i)]			
			category = Category(name= nameCategory, maxvalue = int(maxvalue), minvalue = int(minvalue), description = descriptionCat, project= project)
			category.save()
		#Flag to indicate if the story is a copy	
		if copyFlag:
			relationCategoryNCategory = {} #Dictionary to relate the project categories with the new project categories
			for category in categories: #Categories already created in the other project (might have different name)
				print "Id category: ", category.id
				if bool(request.POST.get("name-" + str(category.id), False)):
					nameCategory = request.POST['name-'+str(category.id)]
					minvalue = category.minvalue
					maxvalue = category.maxvalue
					descriptionCat = category.description
					newcategory = Category(name= nameCategory,maxvalue = int(maxvalue), minvalue = int(minvalue), description = descriptionCat, project= project)
					newcategory.save()
					#This dictionary includes the elements for updating the copy of the story with the new values			
					relationCategoryNCategory[str(category.id)] = {'id':newcategory.id, 'name':nameCategory, 'oldName':category.name}
			resultCopy = copyStory(oldProject, project, relationCategoryNCategory)
			if resultCopy != True:
				return {"status":"error","message": resultCopy}
		else:
			#When the story is edited, handles the change on the settings for the categories.
			for category in categories: #Categories already created in the other project (might have different name)
				nameCategory = request.POST['name-'+str(category.id)]
				descriptionCategory = request.POST['descriptionCategory-'+str(category.id)]
				if category.name != nameCategory:
					#Modification of the reportCategories after changing the name of the category
					reportCategories = ReportCategory.objects.filter(name = category.name)
					if len(reportCategories) > 0:
						for reportCategory in reportCategories:
							reportCategory.name = nameCategory
							reportCategory.save()
					editNameCategory(project, category.name, nameCategory)
				if category.description != descriptionCategory:
					category.description = descriptionCategory;
				category.name = nameCategory
				category.save()
		return {"status":"ok","project":project.id}
	except Exception as e:
		return {"status":"error","message": str(e)}

def editNameCategory(project, oldName, newName):
	'''
	Rename the category name on the xml files to make aware the flash side that the categories has been modified.
	'''
	folderpath = Path(settings.MEDIA_ROOT).child('stories').child(str(project.id))
	nodes = Node.objects.filter(project__id = project.id)
	for node in nodes:
		nodeXMLFile = folderpath.child('node'+str(node.id)+'.xml')
		tree = ET.parse(nodeXMLFile)
		root = tree.getroot()
		#Find the element and change the name
		for report in root.iter('reporting'):
			for child in report:
				if child.attrib['name'] == oldName:
					child.attrib['name'] = newName
		tree.write(nodeXMLFile)
	return 1

def updateColorOptionNode(xmlFile, color):
	'''
	Open the xml file of the node and modify the color for the options of the node
	'''
	color = color.replace("#","0x")
	tree = ET.parse(xmlFile)
	root = tree.getroot()
	for items in root.findall('options'):
		for item in items.findall('item'):
			item.attrib['backgroundColor'] = color
	tree.write(xmlFile)
	return



def updateTreeJsonName(treeFile, nodeId, newName):
	'''
		Update the JSON file for the connection of the node, with the new value 
		of the id's for the nodes. (Use when the story is published)
	'''
	try:
		
		jsonData = open(treeFile)		
		data = json.load(jsonData)
		jsonData.close()
		jsonTree = json.loads(data)
		#get the Layer
		layer = jsonTree["children"][0]
		if not layer["className"] == "Layer":
			return -1
		storeLayer = []
		while(len(jsonTree["children"][0]["children"])> 0):
			element = jsonTree["children"][0]["children"].pop()
			if element["className"]=="Group":
				if element["attrs"]["id"] == ("group_" + str(nodeId)):
					element["children"][1]["attrs"]["text"] = newName			
			storeLayer.append(element)				
		jsonTree["children"][0]["children"] = storeLayer
		jsonDuplicate = json.dumps(jsonTree)
		#print json.dumps(jsonTree,indent = 4, sort_keys= True)
		result= '"' +jsonDuplicate.replace('"','\\"') + '"'		
		with open(treeFile, "w") as f:
			f.write(result)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print "ERROR ", str(e)
		print(exc_type, fname, exc_tb.tb_lineno)


def resultTemplate(xmlString):
	'''
	Create the context to show the results of the nodes selected with the categories
	'''
	xmlSelectionInfo = ET.parse(xmlString)
	xmlSelectionInfo = xmlSelectionInfo.getroot()
	dictCategories = {} #Create a dictionary to store the content of the categories
	try:
		tempOption = None
		for node in xmlSelectionInfo.iter('node'):
			nodeId = int(node[0].text)
			option = node[1].text
			tempOption = option
			nodeSelected = Node.objects.get(id = nodeId)
			if tempOption != "end" and tempOption != "next":
				#Calculate average maximum minimum
				attributes = Attribute.objects.filter(node__id = nodeSelected.id, idAttribute = tempOption, active=True)
				for attribute in attributes:
					reportCategories = ReportCategory.objects.filter(attribute__id = attribute.id)       
					for reportCategory in reportCategories:
						dictCategories[reportCategory.name] = dictCategories.setdefault(reportCategory.name,0) + int(reportCategory.value)
		return dictCategories
	except Exception as e:
		print str(e)
		return e
	return 1