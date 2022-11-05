from functools import cmp_to_key

from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from oj_backend.permissions import Granted, IsAuthenticatedAndReadOnly
from oj_problem.serializers import ProblemBriefSerializer
from oj_user.serializers import UserSerializer
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Contest
from .serializers import ContestDetailSerializer, ContestSerializer


class ContestPagination(LimitOffsetPagination):
    default_limit = 50
    max_limit = 200


class ContestViewSet(ModelViewSet):
    permission_classes = [Granted | IsAuthenticatedAndReadOnly]
    lookup_value_regex = r'\d+'
    pagination_class = ContestPagination
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['id', 'title']
    ordering_fields = ['id', 'title']
    filterset_fields = []

    def get_queryset(self):
        if self.request.user.is_staff:
            return Contest.objects.all()
        return Contest.objects.filter(
            Q(is_hidden=False) | Q(users=self.request.user.id)).distinct()

    def get_serializer_class(self):
        if self.action == 'list':
            return ContestSerializer
        return ContestDetailSerializer

    @action(detail=True, methods=['get'], url_path='ranking')
    def get_ranking(self, request, pk):
        contest = self.get_object()
        if contest.problem_list_mode:
            return Response({'detail': _('No ranking for problem list mode.')})
        if contest.start_time > timezone.now():
            return Response({'detail': _('Contest has not started.')})
        if not (self.request.user.is_staff
                and request.GET.get('force_update') == 'true'):
            data = cache.get(f'contest_ranking_{pk}')
            if data is not None:
                return Response(data)
        contest_problems = {
            i['id']: i['title']
            for i in ProblemBriefSerializer(
                contest.problems.order_by('id'),
                many=True,
            ).data
        }

        res = {'users': [], 'time': timezone.now().isoformat()}

        users = contest.users.all()
        for user in users:
            submissions = user.submissions.filter(
                create_time__range=(contest.start_time, contest.end_time),
                problem_id__in=contest.problems.all(),
            ).order_by('create_time')
            item = {
                **UserSerializer(user).data, 'latest_submit': 0,
                'problems': []
            }
            problems = {}
            for submission in submissions:
                if problems.get(submission.problem_id
                                ) is None or submission.score > problems[
                                    submission.problem_id]['score']:
                    problems[submission.problem_id] = {
                        'name': contest_problems[submission.problem_id],
                        'status': submission.status,
                        'score': submission.score,
                        'time': submission.create_time.isoformat(),
                        'submission_id': submission.id,
                    }
                    item['latest_submit'] = max(
                        item['latest_submit'],
                        submission.create_time.timestamp(),
                    )
            item['score'] = sum([i['score'] for i in problems.values()])
            for id, problem in problems.items():
                problem['id'] = id
                item['problems'].append(problem)
            res['users'].append(item)

        res['users'].sort(key=cmp_to_key(
            lambda x, y: x['score'] > y['score'] if x['score'] != y[
                'score'] else x['latest_submit'] < y['latest_submit']))
        for i in res['users']:
            i.pop('latest_submit')

        cache.set(
            f'contest_ranking_{pk}',
            res,
            60 if contest.end_time > timezone.now() else 86400,
        )

        return Response(res)

    @action(detail=True,
            methods=['post'],
            permission_classes=[IsAuthenticated],
            url_path='sign_up')
    def sign_up(self, request, pk):
        contest = self.get_object()
        if not contest.allow_sign_up:
            raise ValidationError(_('The contest disallows sign up.'))
        elif contest.end_time < timezone.now():
            raise ValidationError(_('The contest is over.'))
        contest.users.add(request.user)
        return Response(status=204)
