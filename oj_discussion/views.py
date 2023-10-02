from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from oj_backend.permissions import (Granted, IsAuthenticatedAndReadCreate,
                                    Captcha)
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Discussion, Reply
from .serializers import DiscussionSerializer, ReplySerializer, ReplyBriefSerializer
from oj_contest.models import Contest


class DiscussionPagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 100


class ReplyPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 100


class DiscussionViewSet(ReadOnlyModelViewSet):
    permission_classes = [Granted | IsAuthenticatedAndReadCreate, Captcha]
    permission = scene = 'discussion'
    pagination_class = DiscussionPagination
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ['id', 'title']
    filterset_fields = [
        'title', 'related_problem__id', 'related_contest__id',
        'author__username'
    ]
    ordering_fields = ['create_time', 'update_time']

    def get_queryset(self):
        site_settings = cache.get('site_settings')
        if not site_settings.get('enableDiscussion'):
            queryset = Discussion.objects.none()
        elif self.permission in self.request.user.permissions:
            queryset = Discussion.objects
        else:
            processing_contest = Contest.objects.filter(
                start_time__lt=timezone.now(), end_time__gt=timezone.now())
            queryset = Discussion.objects
            # queryset = queryset.exclude(Q(_is_hidden=True))
            queryset = queryset.exclude(
                Q(related_problem___is_hidden=True)
                | Q(related_problem___hide_discussions=True)
                | Q(related_problem__contests__contest__in=processing_contest))
            queryset = queryset.exclude(
                Q(related_contest__is_hidden=True)
                | Q(related_contest__in=processing_contest))
            # queryset = queryset | Discussion.objects.filter(
            #     Q(author=self.request.user))
            queryset = queryset.distinct()
        return queryset.order_by('-id')

    def get_serializer_class(self):
        return DiscussionSerializer

    def create(self, request, *args, **kwargs):
        site_settings = cache.get('site_settings')
        if not site_settings.get('enableDiscussion'):
            return Response({'detail': '讨论功能已关闭'}, status=403)
        data = request.data
        discussion = Discussion(title=data['title'], author=request.user)
        if data.get('related_content_type') == 'problem':
            discussion.related_problem_id = data['related_content_id']
        elif data.get('related_content_type') == 'contest':
            discussion.related_contest_id = data['related_content_id']
        discussion.save()
        reply = Reply(content=data['content'],
                      author=request.user,
                      discussion=discussion)
        reply.save()
        return Response({'id': discussion.id}, status=201)

    @action(detail=True, methods=['get', 'post'], url_path='reply')
    def get_reply(self, request, pk=None):
        site_settings = cache.get('site_settings')
        if not site_settings.get('enableDiscussion'):
            return Response({'detail': '讨论功能已关闭'}, status=403)
        if request.method == 'POST':
            data = request.data
            discussion = self.get_object()
            reply = Reply(content=data['content'],
                          author=request.user,
                          discussion=discussion)
            if data.get('reply_to'):
                reply_to = Reply.objects.filter(id=data['reply_to'])
                if reply_to.exists():
                    reply_to = reply_to.first()
                    if reply_to.discussion == discussion:
                        reply.reply_to = reply_to
            reply.save()
            return Response(status=201)
        paginator = ReplyPagination()
        discussion = self.get_object()
        queryset = discussion.replies.order_by('id')
        results = paginator.paginate_queryset(queryset, request)
        serializer = ReplySerializer(results, many=True)
        return Response(serializer.data)