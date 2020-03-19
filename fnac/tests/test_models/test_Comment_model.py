import pytest

from fnac.models import Comment


@pytest.fixture(scope="module")
def comment_text():
    return "Shipping Time\n2 Working Days"


@pytest.mark.django_db
class TestComment:
    @pytest.fixture()
    def existing_comment(self, django_db_blocker, comment_text):
        with django_db_blocker.unblock():
            comment, _ = Comment.objects.get_or_create(id=1)
            comment.comment = comment_text
            comment.save()
            yield comment

    @pytest.mark.django_db
    def test_get_comment(self, existing_comment):
        assert isinstance(Comment.objects.get_comment(), Comment)

    @pytest.mark.django_db
    def test_get_comment_text(self, existing_comment, comment_text):
        assert Comment.objects.get_comment_text() == comment_text

    @pytest.mark.django_db
    def test_set_comment_text(self, existing_comment):
        new_text = "A new shipping policy.\nThree day delivery."
        Comment.objects.set_comment_text(new_text)
        assert Comment.objects.get_comment_text() == new_text


class TestCommentWhenNoneExists:
    @pytest.mark.django_db
    def test_get_comment_when_none_exists(self):
        assert isinstance(Comment.objects.get_comment(), Comment)

    @pytest.mark.django_db
    def test_get_comment_text_when_none_exists(self):
        assert Comment.objects.get_comment_text() == ""

    @pytest.mark.django_db
    def test_set_comment_text_when_none_exists(self, comment_text):
        Comment.objects.set_comment_text(comment_text)
        assert Comment.objects.get_comment_text() == comment_text
