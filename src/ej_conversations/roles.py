from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from hyperpython import a
from hyperpython.django import csrf_input

from ej.roles import with_template
from . import models


#
# Conversation roles
#
@with_template(models.Conversation, role='card')
def conversation_card(conversation, request=None, url=None, board=None, **kwargs):
    """
    Render a round card representing a conversation in a list.
    """

    user = getattr(request, 'user', None)
    is_author = conversation.author == user
    moderate_url = None
    return {
        'conversation': conversation,
        'url': url or conversation.get_absolute_url(board=board),
        'tags': conversation.tags.all(),
        'n_comments': conversation.approved_comments.count(),
        'n_votes': conversation.vote_count(),
        'n_followers': conversation.followers.count(),
        'moderate_url': moderate_url,
        'is_author': is_author,
        **kwargs,
    }


@with_template(models.Conversation, role='balloon')
def conversation_balloon(conversation, request=None, **kwargs):
    """
    Render details of a conversation inside a conversation balloon.
    """

    user = getattr(request, 'user', None)
    favorites = models.FavoriteConversation.objects
    is_authenticated = getattr(user, 'is_authenticated', False)
    is_favorite = is_authenticated and conversation.is_favorite(user)
    tags = list(map(str, conversation.tags.all()[:3]))
    return {
        'conversation': conversation,
        'tags': tags,
        'comments_count': conversation.approved_comments.count(),
        'votes_count': conversation.votes.count(),
        'favorites_count': favorites.filter(conversation=conversation).count(),
        'user': user,
        'csrf_input': csrf_input(request),
        'show_user_actions': is_authenticated,
        'is_favorite': is_favorite,
        **kwargs,
    }


#
# Comments
#
@with_template(models.Comment, role='card')
def comment_card(comment, request=None, **kwargs):
    """
    Render comment information inside a comment card.
    """

    user = getattr(request, 'user', None)
    is_authenticated = getattr(user, 'is_authenticated', False)
    total = comment.conversation.approved_comments.count()
    remaining = total - comment.conversation.user_votes(user).count()
    voted = total - remaining + 1

    login = reverse('auth:login')
    comment_url = comment.conversation.get_absolute_url()
    login_anchor = a(_('login'), href=f'{login}?next={comment_url}')
    return {
        'comment': comment,
        'total': total,
        'voted': voted,
        'show_user_actions': is_authenticated,
        'csrf_input': csrf_input(request),
        'login_anchor': login_anchor,
        **kwargs,
    }


@with_template(models.Comment, role='moderate')
def comment_moderate(comment, request=None, **kwargs):
    """
    Render a comment inside a moderation card.
    """

    return {
        'comment': comment,
        'csrf_input': csrf_input(request),
        **kwargs,
    }


@with_template(models.Comment, role='list-item')
def comment_list_item(comment, **kwargs):
    """
    Show each comment as an item in a list of comments.
    """

    return {
        'comment': comment,
        'content': comment.content,
        'creation_date': comment.created.strftime('%d-%m-%Y às %Hh %M'),
        'conversation_url': comment.conversation.get_absolute_url(),

        # Votes
        'agree': comment.agree_count,
        'skip': comment.skip_count,
        'disagree': comment.disagree_count,
    }
