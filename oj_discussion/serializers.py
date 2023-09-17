from rest_framework import serializers

from .models import Discussion, Reply
from oj_user.serializers import UserBriefSerializer
from oj_problem.serializers import ProblemSerializer
from oj_contest.serializers import ContestSerializer


class DiscussionSerializer(serializers.ModelSerializer):
    author = UserBriefSerializer()
    related_problem = ProblemSerializer()
    related_contest = ContestSerializer()

    reply_count = serializers.SerializerMethodField()
    latest_reply_time = serializers.SerializerMethodField()

    def get_reply_count(self, obj):
        return obj.replies.count()

    def get_latest_reply_time(self, obj):
        return obj.replies.order_by('-create_time').first().create_time

    class Meta:
        model = Discussion
        fields = [
            'id', 'title', 'create_time', 'reply_count', 'latest_reply_time',
            'related_problem', 'related_contest', 'author'
        ]


class DiscussionBriefSerializer(serializers.ModelSerializer):
    author = UserBriefSerializer()
    problem = ProblemSerializer()
    contest = ContestSerializer()

    class Meta:
        model = Discussion
        fields = [
            'id', 'title', 'create_time', 'update_time', 'problem', 'contest',
            'author'
        ]


class ReplyBriefSerializer(serializers.ModelSerializer):
    author = UserBriefSerializer()

    class Meta:
        model = Reply
        fields = ['id', 'author']


class ReplySerializer(serializers.ModelSerializer):
    author = UserBriefSerializer()
    reply_to = ReplyBriefSerializer()

    class Meta:
        model = Reply
        fields = [
            'id', 'content', 'create_time', 'update_time', 'author', 'reply_to'
        ]
