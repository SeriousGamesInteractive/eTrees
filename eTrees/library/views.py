# Create your views here.
import os
from django.conf import settings
from django.shortcuts import render,redirect
from django.core.files import File
from django.contrib.auth.decorators import login_required
from account.models import Trainer
from .models import ResourcesLibrary, AudioAsset, GraphicAsset, AnimationAsset, BackgroundAsset
from .utils import buildXMLAssetFile
#Method to create a new folder and save the assets inside that folder. 
#The name of the folder will be related with the library id
@login_required(login_url='/login')
def generate_filename(instance, filename):
	'''
	Method to create a new folder and save the assets inside that folder. 
	The name of the folder will be related with the library id
	'''
	filename = filename.encode('ascii','ignore')
	result = filename[filename.find('.'):]
	id = ResourcesLibrary.objects.all().order_by('-pk')[:1]
	if not id:
		nid = 1
	else:
		nid =int(id[0].pk) + 1    
	return 'media/assets/'+ str(nid) + "" + result

@login_required(login_url='/login')
def LibraryView(request):
	'''
	Controller for the library view where the list of libraries are shown and the control of delete them or showing are handled.
	'''
	trainers = Trainer.objects.filter(admin__id = request.user.id)
	trainerUser = Trainer.objects.filter(user__id = request.user.id)
	if len(trainerUser) > 0:
		trainers = Trainer.objects.filter(admin__id = trainerUser[0].admin.id).exclude(id = trainerUser[0].id)	

	if request.method == 'POST':		
		name_lib = request.POST['library_name']
		description_lib = request.POST['library_description']
		resource = ResourcesLibrary(name = name_lib,description = description_lib, owner_id = request.user.id)
		resource.save()
		#Initialize the library everytime is opened 
		assetPath = os.path.join(settings.MEDIA_ROOT, "assets",str(resource.id))
		if not os.path.exists(assetPath): 
			os.makedirs(assetPath)
		buildXMLAssetFile(resource.id)
		resource.user.add(request.user)

		#Give access to the library to the trianers selected
		for trainer in request.POST.getlist('trainers'):
			resource.user.add(Trainer.objects.get(id=trainer).user)
		#Check if it is a trainer and add the admin
		if len(trainerUser)>0: # if true, the user is a trainer not admin
			adminModel = trainerUser[0].admin		
			resource.user.add(adminModel)

		#Check the folder assets/library to insert the asset content in that folder
		newpath = os.path.join(settings.MEDIA_ROOT, "assets",str(resource.id))
		if not os.path.exists(newpath):
			os.makedirs(newpath)
		return redirect('admin_newlibrary',library=resource.id)
	#Get the libraries which the user can have access
	libraryList = ResourcesLibrary.objects.filter(user__id__exact = request.user.id)
	return render(request,'library/library.html',{'libraries':libraryList,'trainers':trainers})


@login_required(login_url='/login')
def NewLibraryView(request,library):
	'''
	Controller to manage the saving of the different assets for the library. 
	Each library has a folder named with the id of the library in the database and inside that folder, the controller creates
	several ones respected to the type of asset. In addition, a xml filde is generated to communicate the flash the content of the library.
	'''
	#Returning the content of the database to show the assets already uploaded.
	libraryDB = ResourcesLibrary.objects.get(id=library)
	audioList = AudioAsset.objects.filter(library_id__exact=library).order_by('modified')
	graphicList = GraphicAsset.objects.filter(library_id__exact=library).order_by('modified')
	animationList = AnimationAsset.objects.filter(library_id__exact=library).order_by('modified')
	backgroundList = BackgroundAsset.objects.filter(library_id__exact=library).order_by('modified')
	
	#Build json for the multiple uploading gaphic feature
	graphicListJson = graphicList
	if request.method == 'POST':
		filename = fileExt = database = fileupload = typeAsset= ""
		resourceLib = ResourcesLibrary.objects.filter(id = library)[0]
		try:
			if request.POST['form-type'] == u"audio":
				#Uploading of the audio assets, using the tag multiple html to upload several files at the same time.
				if request.FILES.get('file_audio_multiple'):				
					filesupload = request.FILES.getlist('file_audio_multiple')
					typeAsset = "audio"
					for fileupload in filesupload:
						filename, fileExt = os.path.splitext(fileupload.name)
						if "mp3" not in fileExt.lower():
							return render(request,'library/newlibrary.html',{"library":libraryDB,"audiolist":audioList,"graphiclist":graphicList,"animationlist":animationList,"backgroundlist":backgroundList,
							"message":"Audio file extension is not allowed.", "type":typeAsset})					
						database = AudioAsset(name = filename, library = resourceLib)
						database.save()
						saveFile(fileupload,fileExt,library,database,request.POST['form-type'])						
					#Create the xml file for the respective library created 
					buildXMLAssetFile(library)					
					return render(request,'library/newlibrary.html',{"library":libraryDB,"audiolist":audioList,"graphiclist":graphicListJson,"animationlist":animationList,"backgroundlist":backgroundList,
					"messagegreen":"Asset saved!!", "type":typeAsset})			
			elif request.POST['form-type'] == u"graphic":
				#Uploading of the graphic assets, using the tag multiple html to upload several files at the same time.
				if request.FILES.get('file_graphic_multiple'):
					filesupload = request.FILES.getlist('file_graphic_multiple')
					typeAsset = 'graphic'
					for fileupload in filesupload:
						#Check the extension
						filename, fileExt = os.path.splitext(fileupload.name)						
						if ("png" not in fileExt.lower()) and ("jpg" not in fileExt.lower()):
							return render(request,'library/newlibrary.html',{"library":libraryDB,"audiolist":audioList,"graphiclist":graphicList,"animationlist":animationList,"backgroundlist":backgroundList,
				"message":"Graphic file extension is not allowed.", "type":typeAsset})	
						checkName = GraphicAsset.objects.filter(library__id = libraryDB.id,name = filename).count()
						if checkName > 0:
							return render(request,'library/newlibrary.html',{"library":libraryDB,"audiolist":audioList,"graphiclist":graphicList,"animationlist":animationList,"backgroundlist":backgroundList,
				"message":"The name of file: "+filename + " already exist in the system", "type":typeAsset})					
						database = GraphicAsset(name = filename, library = resourceLib)
						database.save()
						saveFile(fileupload,fileExt,library,database,request.POST['form-type'])						
					#Create the xml file for the respective library created 
					buildXMLAssetFile(library)					
					return render(request,'library/newlibrary.html',{"library":libraryDB,"audiolist":audioList,"graphiclist":graphicListJson,"animationlist":animationList,"backgroundlist":backgroundList,
					"messagegreen":"Asset saved!!", "type":typeAsset})			
			elif request.POST['form-type'] == u"animation":
				#Uploading of the animation assets, using the tag multiple html to upload several files at the same time.
				if request.FILES.get('file_animation_multiple'):
					filesupload = request.FILES.getlist('file_animation_multiple')
					typeAsset = 'animation'
					for fileupload in filesupload:
						filename, fileExt = os.path.splitext(fileupload.name)
						if "swf" not in fileExt.lower():
							return render(request,'library/newlibrary.html',{"library":libraryDB,"audiolist":audioList,"graphiclist":graphicList,"animationlist":animationList,"backgroundlist":backgroundList,
					"message":"Animation file extension is not allowed.", "type":typeAsset})
							pass # TODO finish the return message when the file is incompatible
						database = AnimationAsset(name = filename, library = resourceLib)		
						database.save()
						saveFile(fileupload,fileExt,library,database,request.POST['form-type'])
					#Create the xml file for the respective library created 
					buildXMLAssetFile(library)					
					return render(request,'library/newlibrary.html',{"library":libraryDB,"audiolist":audioList,"graphiclist":graphicListJson,"animationlist":animationList,"backgroundlist":backgroundList,
					"messagegreen":"Asset saved!!", "type":typeAsset})	
			elif request.POST['form-type'] == u"background":
				#Uploading of the background assets, using the tag multiple html to upload several files at the same time.
				if request.FILES.get('file_background_multiple'):
					filesupload = request.FILES.getlist('file_background_multiple')
					typeAsset = 'background'
					for fileupload in filesupload:
						#Check the extension
						filename, fileExt = os.path.splitext(fileupload.name)
						if ("png" not in fileExt.lower()) and ("jpg" not in fileExt.lower()):
							return render(request,'library/newlibrary.html',{"library":libraryDB,"audiolist":audioList,"graphiclist":graphicList,"animationlist":animationList,"backgroundlist":backgroundList,
				"message":"Background file extension is not allowed.", "type":typeAsset})							 
						checkName = BackgroundAsset.objects.filter(library__id = libraryDB.id,name = filename).count()
						if checkName > 0:
							return render(request,'library/newlibrary.html',{"library":libraryDB,"audiolist":audioList,"graphiclist":graphicList,"animationlist":animationList,"backgroundlist":backgroundList,
				"message":"The name of file: "+filename + " already exist in the system", "type":typeAsset})					
						database = BackgroundAsset(name = filename, library = resourceLib)
						database.save()
						saveFile(fileupload,fileExt,library,database,request.POST['form-type'])
					#Create the xml file for the respective library created 
					buildXMLAssetFile(library)
					print "Finish"
					return render(request,'library/newlibrary.html',{"library":libraryDB,"audiolist":audioList,"graphiclist":graphicListJson,"animationlist":animationList,"backgroundlist":backgroundList,
					"messagegreen":"Asset saved!!", "type":typeAsset})
			if fileupload == "":	
				return render(request,'library/newlibrary.html',{"library":libraryDB,"audiolist":audioList,"graphiclist":graphicList,"animationlist":animationList,"backgroundlist":backgroundList})
			return render(request,'library/newlibrary.html',{"library":libraryDB,"audiolist":audioList,"graphiclist":graphicListJson,"animationlist":animationList,"backgroundlist":backgroundList,
					"messagegreen":"Asset saved!!", "type":typeAsset})
		except Exception as e:
				return render(request,'library/newlibrary.html',{"library":libraryDB,"audiolist":audioList,"graphiclist":graphicListJson,"animationlist":animationList,"backgroundlist":backgroundList,
				"message":"An error has occured: %s " % (e)})

	#Obtain the assets from each content with the id of the library 
	return render(request,'library/newlibrary.html',{"library":libraryDB,"audiolist":audioList,"graphiclist":graphicListJson,"animationlist":animationList,"backgroundlist":backgroundList})


def saveFile(fileupload,fileExt,library,database,typeAsset):
	'''
		Create the folder and save the content of the file in the folder based on the parameters.

		parameters:
			fileupload -> the file to be saved
			fileExt -> the extension of the file (ex. .png)
			library -> the id of the library
			database -> the table to save the file ( BackgroundAsset, AnimationAsset, GraphicAsset and AudioAsset) 
			typeAsset -> type of asset to be save (audio, graphic, animation, background)
	'''
	try:
		filepath = os.path.join(settings.MEDIA_ROOT, "assets",str(library),typeAsset)
		if not os.path.exists(filepath): 
			os.makedirs(filepath)
		#Path for the file
		filename = str(database.id) + fileExt
		filepath = filepath +"/"+ filename		
		#Save the file in the folder and the information of the file in the database
		database.pathFile.save(filepath,File(fileupload),save=True)
	except Exception as e:	
		raise e