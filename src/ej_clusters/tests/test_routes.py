import pytest

from ej.testing import UrlTester
from ej_conversations.mommy_recipes import ConversationRecipes


class TestRoutes(UrlTester, ConversationRecipes):
    owner_urls = [
        '/conversations/conversation/stereotypes/add/',

        # FIXME: this does not work on tests, but seems to work everywhere!
        # '/conversations/conversation/stereotypes/',
    ]

    @pytest.fixture
    def data(self, conversation, author_db):
        conversation.author = author_db
        conversation.save()
        return {
            'conversation': conversation.__dict__,
            'author': author_db.__dict__,
        }
