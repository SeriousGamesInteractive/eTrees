__author__ = 'Felix Rubio (at) SGI'

import os
import sys
import json
import shutil
import re
from unipath import Path

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string,get_template
from django.utils.html import strip_tags

from createstory.models import Node, ClosureTable, Attribute, ReportCategory
'''
	AUXILIAR METHODS FOR THE API

'''

#COnstant to place the elements in the connector tool
POSITIONCIRCLEOPTIONS ={	
    "a" : {"x":190,"y":30},
    "b" : {"x":190,"y":80},
    "c" : {"x":190,"y":130},
    "n" : {"x":190,"y":80}
}
POSITIONTEXTOPTIONS = {
    "a" : {"x":185,"y":0},
    "b" : {"x":185,"y":50},
    "c" : {"x":185,"y":100},
    "n" : {"x":185,"y":50}
}

###### SEND EMAIL #####
def sendEmail(email, url, username, storyname, extraMessage):
	try:
		template =get_template('email_template.html')
		#context =Context({"url":url,"user":username,"storyname":storyname})
		context = {"url":url,"user":username,"storyname":storyname, "extraMessage": extraMessage}
		#content = template.render(context)
		print "The url: ",url
		print "User ",username
		renderpage = render_to_string('email_template.html',context)
		email = EmailMultiAlternatives('Etrees story',
			strip_tags(renderpage),'etrees@seriousgames.net',
			to=[email])
		email.attach_alternative(renderpage,"text/html")
		email.send()
		return "success"
	except Exception as e:
		return str(e)
	return


def updateTreeJson(treeFile,translateNodeId):
	'''
		Update the JSON file for the connection of the node, with the new value 
		of the id's for the nodes. (Use when the story is published)
	'''
	try:
		jsonData = open(treeFile)		
		data = json.load(jsonData)
		jsonTree = json.loads(data)
		#get the Layer
		layer = jsonTree["children"][0]
		if not layer["className"] == "Layer":
			return -1
		
		for element in layer["children"]:
			idelement = element["attrs"]["id"]
			idelement = replaceNodeId(idelement,translateNodeId)
			element["attrs"]["id"] = idelement
			if element["className"]=="Group":
				for groupElement in element["children"]:
					if groupElement["attrs"].get("id"):
						idelement = groupElement["attrs"]["id"]
						idelement = replaceNodeId(idelement,translateNodeId)
						groupElement["attrs"]["id"] = idelement	
		jsonDuplicate = json.dumps(jsonTree)
		result= '"' +jsonDuplicate.replace('"','\\"') + '"'		
		with open(treeFile,"w") as f:
			f.write(result)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(exc_type, fname, exc_tb.tb_lineno)



def recalculateTree(node, deleteNode = False):
	'''
	Rewrite the tree.json observing the modification of the options
	'''
	node = Node.objects.get(id=node)
	story = node.project
	treeFile = Path(settings.MEDIA_ROOT).child('stories').child(str(story.id)).child('tree.json')
	treeResultFile = Path(settings.MEDIA_ROOT).child('stories').child(str(story.id)).child('tree_test.json')
	optionsNode = Attribute.objects.filter(node__id = node.id,active=True)
	listOptions = []
	for optionNode in optionsNode:
		listOptions.append(optionNode.idAttribute)
	#If the listoptions is empty, a next button has to be added (normal or initial node)	
	if len(listOptions) == 0 and node.type != 2 and not deleteNode:
		listOptions.append("n")
	if os.path.exists(treeFile):
		try:
			#Process to convert JSON to python Object
			jsonString = open(treeFile,'r')
			jsonLoad = json.load(jsonString)
			data = json.loads(jsonLoad)
			jsonString.close()
			##########################
			#First remove the connection of the node
			linesCache = []
			while(len(data["children"][0]["children"])> 0):
				lines = data["children"][0]["children"].pop()

				if lines["className"] == "Line":
					idLine = lines["attrs"]["id"]
					idLineNode = idLine.split("-")[1].split("_")[1] #example id : line-b_1-4
					idConnectedNode = idLine.split("-")[2]
					optionLine =idLine[5:6]
					#Check the start point of the line. 
					#Also check the end point when the node has to be deleted
					if int(node.id) != int(idLineNode) and ( not deleteNode or int(node.id) != int(idConnectedNode)):
						linesCache.append(lines)						
					elif optionLine in listOptions:
						linesCache.append(lines) #Delete the line
				else:
					linesCache.append(lines)
			data["children"][0]["children"] = linesCache
			#Second check the option of the node
			if deleteNode: 	# Delete the node in the tree connection,
							# loop through all the groups and delete the group with the node.id as id
				resultGroup = []
				while(len(data["children"][0]["children"]) > 0):
					group = data["children"][0]["children"].pop()
					if group["className"] == "Group":
						idGroup = group["attrs"]["id"].split("_")[1]
						if int(idGroup) != int(node.id):
							resultGroup.append(group)
					else:
						resultGroup.append(group)
				data["children"][0]["children"] = resultGroup
			else:
				nodeJsonId = -1
				for i in xrange(len(data["children"][0]["children"])):
					groups = data["children"][0]["children"][i]
					if groups["className"] == "Group":						
						idGroup = groups["attrs"]["id"].split("_")[1]#id example: group_2
						if idGroup == str(node.id):
							nodeJsonId = i
				print nodeJsonId
				if nodeJsonId != -1: 
					#The aim is to remove the circle and text of the elements disables
					cacheGroup = []
					storeOption = []
					while(len(data["children"][0]["children"][nodeJsonId]["children"]) > 0):
						options = data["children"][0]["children"][nodeJsonId]["children"].pop()
						if options["className"] == "Text" and options["attrs"]["name"] == "options":
							idOption = options["attrs"]["text"]
							print "Text opt: ", idOption
							print "listOptions ", listOptions
							if idOption in listOptions:					
								storeOption.append(idOption) #store the option to delete it on the listOptions
								cacheGroup.append(options) #The element is included if the options is contained in the array of available options						
						elif options["className"] == "Circle":
							idOption = options["attrs"]["id"][:1]
							if idOption in listOptions:
								cacheGroup.append(options) #The element is included if the options is contained in the array of available options
								storeOption.append(idOption)
						else:
							cacheGroup.append(options)
					#Remove the options already existed on the tree.json
					storeOption = list(set(storeOption))
					listOptions = list(set(listOptions) - set(storeOption))
					data["children"][0]["children"][nodeJsonId]["children"] = cacheGroup			

					print "The options ", listOptions
					#Add the elements missing in the canvas
					for options in listOptions:
						positionCircle = POSITIONCIRCLEOPTIONS[options]
						positionText =  POSITIONTEXTOPTIONS[options]
						circle = {}
						circle["className"] = "Circle"
						circle["attrs"]= {}
						circle["attrs"]["x"] = positionCircle["x"]
						circle["attrs"]["y"] = positionCircle["y"]
						circle["attrs"]["radius"] = 6
						circle["attrs"]["fill"] = "blue"
						circle["attrs"]["stroke"] = "black"
						circle["attrs"]["strokeWidth"] = 1
						
						circle["attrs"]["id"] = str(options) + "_" + str(node.id)
						circle["attrs"]["name"] = "connection"
						circle["attrs"]["isConnected"]= False
						textOption = {}
						textOption["className"] = "Text"
						textOption["attrs"] = {}
						textOption["attrs"]["x"] = positionText["x"]
						textOption["attrs"]["y"] = positionText["y"]
						textOption["attrs"]["text"] = options
						textOption["attrs"]["fontSize"] = 18
						textOption["attrs"]["fontFamily"] = "Calibri"
						textOption["attrs"]["fill"] = "black"
						textOption["attrs"]["width"] = "auto"
						textOption["attrs"]["height"] = "auto"
						textOption["attrs"]["name"] = 'options'

						data["children"][0]["children"][nodeJsonId]["children"].append(circle)
						data["children"][0]["children"][nodeJsonId]["children"].append(textOption)
			#Save the json updated on the tree.json file
			#with open(treeFile, "w") as f:
			#	f.write(json.dumps(json.dumps(data)))
			jsonResult = json.dumps(data);
			#print json.dumps(data,indent = 4, sort_keys= True)
			result= '"' +jsonResult.replace('"','\\"') + '"'		
			with open(treeFile,"w") as f:
				f.write(result)


		except Exception as e:
			print str(e)
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)
			return
	return

def deleteContentStory(project,folder):
	'''
	Delete all the content save it on the folder
	'''    
	folderpath = Path(settings.MEDIA_ROOT).child(folder).child(str(project.id))
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

def replaceNodeId(idelement, translateNodeId):
	idnodes = map(int,re.findall(r'\d+',idelement))					
	for idnode in idnodes:
		 idelement =idelement.replace(str(idnode),str(translateNodeId[idnode]))
	return idelement



def getExtendedPath(path):
	if path.find("eTrees") == -1:
		return path
	else:
		return path[path.find("eTrees")+len("eTrees"):]

