import time

from django.conf.urls import url, include
from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import routers, serializers, viewsets

from .models import Conversation, Comment, Vote


User = get_user_model()


class AuthorSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'name', 'image_url')

    def get_name(self, obj):
        return obj.get_full_name()


class VoteSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Vote
        fields = ('id', 'author', 'comment', 'value')


class ConversationSimpleReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ('id', 'title', 'description', 'total_votes', 'created_at',)


class CommentReportSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    agreement_consensus = serializers.SerializerMethodField()
    disagreement_consensus = serializers.SerializerMethodField()
    uncertainty = serializers.SerializerMethodField()
    conversation = ConversationSimpleReportSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'author', 'content', 'created_at', 'total_votes',
                  'agree_votes', 'disagree_votes', 'pass_votes', 'approval',
                  'agreement_consensus', 'disagreement_consensus', 'uncertainty',
                  'conversation', 'rejection_reason')

    def get_agreement_consensus(self, obj):
        try:
            return (obj.agree_votes/obj.total_votes > 0.6)
        except ZeroDivisionError:
            return False

    def get_disagreement_consensus(self, obj):
        try:
            return (obj.disagree_votes/obj.total_votes > 0.6)
        except ZeroDivisionError:
            return False

    def get_uncertainty(self, obj):
        try:
            return (obj.pass_votes/obj.total_votes > 0.3)
        except ZeroDivisionError:
            return False


class CommentSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'conversation', 'content', 'polis_id', 'author',
                  'approval', 'votes', 'created_at', 'rejection_reason')
        read_only_fields = ('id', 'author', 'votes')


class ConversationReportSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    comments = CommentReportSerializer(read_only=True, many=True)

    class Meta:
        model = Conversation
        fields = ('id', 'author', 'total_votes', 'agree_votes', 'pass_votes',
                  'disagree_votes', 'pass_votes', 'total_comments',
                  'approved_comments', 'rejected_comments',
                  'unmoderated_comments', 'total_participants', 'comments')


class ConversationSerializer(serializers.ModelSerializer):
    user_participation_ratio = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%d-%m-%Y")
    updated_at = serializers.DateTimeField(format="%d-%m-%Y")

    class Meta:
        model = Conversation
        fields = ('id', 'title', 'description', 'author', 'background_color',
                  'background_image', 'dialog', 'response', 'total_votes',
                  'approved_comments', 'user_participation_ratio', 'created_at',
                  'updated_at', 'polis_url', 'polis_slug', 'is_new', 'position')

    def _get_current_user(self):
        return self.context['request'].user

    def get_user_participation_ratio(self, obj):
        user = self._get_current_user()
        if user.is_authenticated():
            return obj.get_user_participation_ratio(user)
        return
