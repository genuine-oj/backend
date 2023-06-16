from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Problem, TestCase, Tags, ProblemSolve


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'tag_list', 'is_hidden', 'create_time', 'update_time']
    search_fields = ['id', 'title']
    filter_horizontal = ['tags']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    def tag_list(self, obj):
        return u', '.join(o.name for o in obj.tags.all())

    tag_list.short_description = _('tags')


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'problem', 'test_case_id']


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(ProblemSolve)
class ProblemSolveAdmin(admin.ModelAdmin):
    list_display = ['id', 'problem', 'user', 'create_time']
