__author__ = 'Felix Rubio (at) SGI'
import datetime
import json
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from django.shortcuts import render, RequestContext, redirect
from django.http import HttpResponse
from django.conf import settings
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from eTrees.global_constants import Constants
from publishstory.models import ProjectValoration, SessionUser, UserNodeSelection
from createstory.models import Project, Node, ClosureTable, Attribute, Category, ReportCategory
from .models import UniqueUrl



def getRelativePath(path):
    '''
    Auxiliar method to get the relative path
    '''
    if path.find("eTrees") == -1:
        return path
    else:
        return path[path.find("eTrees")+len("eTrees"):]

@csrf_exempt
def get_file(request, code):
    """
    Handles the viewer for the trainee, apart from decrypt the information from the code to get the exactly id of the project
    """
    try:
        if request.method == 'POST':
            result={}
            try:
                if request.POST.get('idnode'):
                    nodeId = request.POST['idnode']
                    option = request.POST["option"]
                    closureTables = ClosureTable.objects.filter(node__id=nodeId)
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
                    result['xmlNode']=getRelativePath(newNode.xmlFile.url);
                    result['nodeId'] = newNode.id
                    result['lastNode'] = lastNode
                elif request.POST.get('storyresult'):
                    #Get the project valoration
                    my_unique = UniqueUrl.objects.get(url=code)
                    my_object_id = my_unique.decode_url(my_unique.url_hash,my_unique.url)[1]
                    projectValoration = ProjectValoration.objects.get(id=my_object_id)
                    
                    if projectValoration.active == False:
                        return render(request,'unique/game_error.html')
                    
                    projectValoration.completed = True
                    projectValoration.save()
                    project = Project.objects.get(id = projectValoration.project.id)
                    #Save the content received by a xml file in the database
                    sessionSave = saveSessionUser(request.POST['storyresult'],projectValoration)
                    if not type(sessionSave) is SessionUser:
                        return HttpResponse(str(sessionSave))
                    siteUrl = settings.SITE_URL
                    result["url"] = siteUrl + "/game/result/" + code + "/" + str(sessionSave.id)
                    return HttpResponse(json.dumps(result),mimetype="application/json")                    
            except Exception as e:
                result["error"] = str(e)
            resultJson = json.dumps(result)
            return HttpResponse(resultJson,mimetype="application/json")
        else:
            my_unique = UniqueUrl.objects.get(url=code)
            #The expiration time has been removed
            #if datetime.date.today() < my_unique.expiration_date:
            siteUrl = settings.SITE_URL
            my_object_id = my_unique.decode_url(my_unique.url_hash,my_unique.url)[1]
            projectValoration = ProjectValoration.objects.get(id=my_object_id)

            if projectValoration.active == False:
                return render(request,'unique/game_error.html')

            project = projectValoration.project
            if project.activate == Constants.DEACTIVATE_PUBLISH:
                return render(request, 'unique/no_game.html', {"project":project})

            flashFolder = "/static/flash/"
            initialNode = Node.objects.get(project__id = project.id,type=1)
            postURL = "/game/"+code 
            return render(request,'unique/game.html',{"SITE_URL":siteUrl,"flashFolder":flashFolder,
                "nodeFile":getRelativePath(initialNode.xmlFile.url),
                "nodeId":initialNode.id,"postURL":postURL}) 
    except Exception as e:
        return HttpResponse(str(e))
        #{"storyname":project.name, "username":projectValoration.user.name})        
    render(request,'unique/game_error.html')


def generate_url(unique_object):
    """
    generate unique url from object id
    """
    #unique_object = ProjectValoration.objects.get(id=object_id)
    try:
        my_unique = UniqueUrl.objects.get(ref_object=unique_object)
    except UniqueUrl.DoesNotExist:
        expirationDate = datetime.date.today() + datetime.timedelta(settings.EXP_DATE_DAYS)
        my_unique = UniqueUrl.objects.create(expiration_date=expirationDate,
            ref_object=unique_object)
        my_unique.encode_url()
    return my_unique                                                                                                                            



def result_trainee(request, code, idsession):
    '''
    Manage the generation of the result for the trainee based on the result obtined from the story. 
    '''
    my_unique = UniqueUrl.objects.get(url=code)
    my_object_id = my_unique.decode_url(my_unique.url_hash,my_unique.url)[1]
    projectValoration = ProjectValoration.objects.get(id=my_object_id)
    project = Project.objects.get(id = projectValoration.project.id)

    #It needs to send the information of the questions answer, the value of the attributes
    nodesSelected = UserNodeSelection.objects.filter(sessionUser__id = idsession)
    dictCategories = {}
    for nodeSelect in nodesSelected:
        if nodeSelect.attributeSelected != "end" and nodeSelect.attributeSelected != "next":
            #Calculate average maximum minimum
            attributes = Attribute.objects.filter(node__id = nodeSelect.node.id, idAttribute = nodeSelect.attributeSelected, active=True)  
            for attribute in attributes:
                reportCategories = ReportCategory.objects.filter(attribute__id = attribute.id)       
                for reportCategory in reportCategories:
                    dictCategories[reportCategory.name] = dictCategories.setdefault(reportCategory.name,0) + int(reportCategory.value)
					
    categories = Category.objects.filter(project__id = project.id)
	
    return render(request,'unique/trainee_result.html',{"code":code, "project":project, "reportCategories":dictCategories, "categories":categories})

def saveSessionUser(xmlString,projectValoration):
    '''
        Read the XML file sent by the flash viewer and create the session for the user
    '''
    xmlSessionInfo = ET.fromstring(xmlString.encode('utf8'))
    startTime = datetime.datetime.now()
    try:
        for child in xmlSessionInfo:
            if child.tag == "starttime":
                startTime = datetime.datetime.fromtimestamp(int(child.text)/1000)
        sessionUser = SessionUser(projectValoration = projectValoration,startTime = startTime, finishTime = now())
        sessionUser.save()
        depthCounter = 0
        tempNodeId = None
        tempOption = None
        for node in xmlSessionInfo.iter('node'):
            nodeId = int(node[0].text)
            option = node[1].text
            tempNodeId = nodeId
            tempOption = option
            nodeSelected = Node.objects.get(id = nodeId)
            usernodeSelection = UserNodeSelection(node = nodeSelected, sessionUser = sessionUser, attributeSelected = option,depth = depthCounter)
            usernodeSelection.save()        
            depthCounter+=1
        if tempOption == "next": #The flash return next and the database has 'n' as a reference
            tempOption = "n"
        closureTable = ClosureTable.objects.get(node__id=tempNodeId,attribute_id = tempOption)
        lastNode = Node.objects.get(id=closureTable.descendant_id)
        usernodeSelection = UserNodeSelection(node = lastNode, sessionUser = sessionUser, attributeSelected ="end",depth = depthCounter)
        usernodeSelection.save()
        return sessionUser
        #temNodeId
    except Exception as e:
        print str(e)
        return e
    return 1