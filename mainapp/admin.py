from django.contrib import admin
from .models import Course,Message,Course_Content,Course_Material

admin.site.register(Course)
admin.site.register(Message)
admin.site.register(Course_Material)
admin.site.register(Course_Content)
