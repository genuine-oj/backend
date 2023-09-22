from django.db.models import Q
from django_filters import rest_framework as filters

from .models import Problem


class ProblemFilter(filters.FilterSet):
    tags = filters.CharFilter(method='filter_by_tags')

    class Meta:
        model = Problem
        fields = ['difficulty']

    def filter_by_tags(self, queryset, name, value):
        tags = value.split(',')  # 假设标签是逗号分隔的字符串
        if len(tags) == 0:
            return queryset
        q = Q(tags__id=tags[0])
        for tag in tags[1:]:
            q &= Q(tags__id=tag)
        return queryset.filter(q).distinct()