from django.contrib import admin

from .models import Submission


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'problem', 'language', 'status', 'score', 'create_time']
    readonly_fields = ['score', 'execute_time', 'execute_memory', 'detail', 'log', 'create_time']
    autocomplete_fields = ['user', 'problem']
