from django.contrib import admin

from .models import Problem, TestCase


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_hidden', 'create_time', 'update_time']
    search_fields = ['title']


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    pass
