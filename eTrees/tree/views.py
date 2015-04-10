# Create your views here.
from django.http import HttpResponse,HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render,render_to_response,redirect
from django.contrib.auth.decorators import login_required
from createstory.models import Project,Node,ClosureTable
from .utils import buildConnectionTree

@login_required(login_url='/login')
def PlaygroundView(request,story):
	'''
		Parameter story, id of the project.
		Obtain the project open from the user login and render the nodes assigned
		to that project 
	'''
	project = Project.objects.get(id=story,user__id__exact = request.user.id )
	nodes = Node.objects.filter(project__id =project.id).order_by("-type")
	if request.method == 'POST':
		#CALCULATE THE CONNECTION AND SAVE THE REFERENCE IN THE DATABASE		
		resultConnection = buildConnectionTree(story)
		if not resultConnection == True:
			#Issue in the result connection
			print resultConnection
			return render(request,'tree/playground.html',{"nodes":nodes,"story":story,"message_error":resultConnection})
		project.canPublish = True
		project.save()
		return redirect('admin_edit_story',story=story)   
		
	if not project:
		return render(request,'404.html')
	
	return render(request,'tree/playground.html',{"nodes":nodes,"story":story})