from django.contrib import admin
from .models import Trainer


class TrainerAdmin(admin.ModelAdmin):
    list_display = ('id','user')
    pass
admin.site.register(Trainer, TrainerAdmin)