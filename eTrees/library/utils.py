__author__ = 'Felix Rubio (at) SGI'

from unipath import Path

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from django.conf import settings

from api.utils import getExtendedPath
from library.models import GraphicAsset, AudioAsset, AnimationAsset, BackgroundAsset, ResourcesLibrary


def buildXMLAssetFile(libraryId):
	'''
		Create the XML file for the assets. From the assets saved, this method generated an XML file in order to 
		communicate the flash tool the content on the library. 
	'''
	resourcesLibrary = ResourcesLibrary.objects.get(id = libraryId)
	assetBackground = BackgroundAsset.objects.filter(library__id=libraryId)
	assetAudio = AudioAsset.objects.filter(library__id=libraryId)
	assetGraphic = GraphicAsset.objects.filter(library__id=libraryId)
	assetAnimation = AnimationAsset.objects.filter(library__id=libraryId)
	root = ET.Element("root")
	#NAME library 
	name = ET.SubElement(root,"name")
	name.text = resourcesLibrary.name
	#BACKGROUND
	background = ET.SubElement(root,"background")
	for element in assetBackground:
		item = ET.SubElement(background,"item")
		item.set("id",str(element.id))
		item.set("name",element.name)
		print "Path background file ", element.pathFile
		item.set("file",getExtendedPath(element.pathFile.path))
	#ANIMATION
	animation = ET.SubElement(root,"animation")
	for element in assetAnimation:
		item = ET.SubElement(animation,"item")
		item.set("id",str(element.id))
		item.set("name",element.name)
		print "Path  ani file ", element.pathFile
		item.set("file",getExtendedPath(element.pathFile.path))
	#GRAPHICS
	graphic = ET.SubElement(root,"image")
	for element in assetGraphic:
		item = ET.SubElement(graphic,"item")
		item.set("id",str(element.id))
		item.set("name",element.name)
		print "Path graphix file ", element.pathFile
		item.set("file",getExtendedPath(element.pathFile.path))
	#AUDIO
	audio = ET.SubElement(root,"sound")
	for element in assetAudio:
		item = ET.SubElement(audio,"item")
		item.set("id",str(element.id))
		item.set("name",element.name)
		item.set("type",element.audioType)
		print "Path audio file ", element.pathFile
		item.set("file",getExtendedPath(element.pathFile.path))
	folderLib = Path(settings.MEDIA_ROOT).child('assets').child(str(libraryId)).child("assets.xml")
	with open(folderLib,'wb+') as f:
		tree = ET.ElementTree(root)
		tree.write(f) #Print out to see the xml file 
		f.close()
