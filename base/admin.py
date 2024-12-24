from django.contrib import admin

from .models import Question, Response, SubQuestion, Section

# Register your models here.

# from .models import Profile

admin.site.register(Question)
admin.site.register(Response)
admin.site.register(SubQuestion)
admin.site.register(Section)
