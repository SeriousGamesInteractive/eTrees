from django.contrib import admin
from .models import ResourcesLibrary, AudioAsset, GraphicAsset, AnimationAsset, BackgroundAsset



class ResourceLibraryAdmin(admin.ModelAdmin):
    list_display = ('id','name')
    pass

class AudioAdmin(admin.ModelAdmin):
	list_display = ('id', 'name')
	pass

class GraphicAdmin(admin.ModelAdmin):
	list_display = ('id', 'name')
	pass

class AnimationAdmin(admin.ModelAdmin):
	list_display = ('id', 'name')
	pass

class BackgroundAdmin(admin.ModelAdmin):
	list_display = ('id', 'name')
	pass

admin.site.register(ResourcesLibrary, ResourceLibraryAdmin)
admin.site.register(AudioAsset, AudioAdmin)
admin.site.register(GraphicAsset, GraphicAdmin)
admin.site.register(AnimationAsset, AnimationAdmin)
admin.site.register(BackgroundAsset, BackgroundAdmin)
