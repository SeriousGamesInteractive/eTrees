from django.contrib import admin
from .models import Node,Project,ClosureTable


class ProjectAdmin(admin.ModelAdmin):
    #list_display = ('title','date','rating')
    pass


class NodeAdmin(admin.ModelAdmin):
    list_display = ('id','name')
    pass


admin.site.register(Node,NodeAdmin)
admin.site.register(Project,ProjectAdmin)

