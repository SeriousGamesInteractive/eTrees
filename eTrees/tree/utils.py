import json
import sys
import os
from unipath import Path
from django.conf import settings
from createstory.models import Node, ClosureTable

def buildConnectionTree(projectId):
	'''
		Create the xml file for the connection of the nodes. 
		Read the json created by the tree tool and save the information in the xml and on the database.
		Parameter:
			projectId: The id of the project.
	'''
	jsonFile= Path(settings.MEDIA_ROOT).child('stories').child(str(projectId)).child('tree.json')
	nodes = Node.objects.filter(project__id=projectId)
	try:

		jsonData = open(jsonFile)
		data = json.load(jsonData)
		jsonTree = json.loads(data)
		#get the Layer
		layer = jsonTree["children"][0]
		if not layer["className"] == "Layer":
			return -1
		#Loof for the groups
		#Modify the value of all connection to False, revaluate the connection
		for node in nodes:
			ClosureTable.objects.filter(node__id=node.id).update(connected = False)

		#Loop for the Lines
		for element in layer["children"]:
			if element["className"] == "Line":
				lineConnection = element["attrs"]["id"].split("-")
				#Get the id of the origin node
				nodeid = int(lineConnection[1].split("_")[1])
				#Get the option of the node, could be (a,b,c or n)
				nodeAttributeId =  lineConnection[1].split("_")[0]
				#Get the id of the node where the origin node is connected to
				nodeidcnt = int(lineConnection[2])
				#print "node1: %d node2: %d" % (nodeid,nodeidcnt)
				node_root = Node.objects.get(id=nodeid)

				#Get the table with descendant_id = 0, new
				closure_table_root = ClosureTable.objects.filter(node__id__exact=node_root.id,attribute_id=nodeAttributeId)				
				if len(closure_table_root) == 0:
					closure_table_root = ClosureTable(node=node_root,descendant_id = nodeidcnt,attribute_id = nodeAttributeId,connected=True)
				else:			
					closure_table_root = closure_table_root[0]
					closure_table_root.descendant_id=  nodeidcnt
					closure_table_root.connected = True
				closure_table_root.save()
		return True
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		return str(e)