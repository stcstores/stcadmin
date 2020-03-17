import pytest

from fnac.models import Comment


@pytest.fixture
def comment():
    return "Shipping Time\n2 Working Days"


@pytest.mark.django_db
def test_set_comment(comment_factory, comment):
    comment_factory.create()
    Comment.objects.set_comment(comment)
    assert Comment.objects.get_comment() == comment


@pytest.mark.django_db
def test_set_comment_when_none_exists(comment):
    Comment.objects.set_comment(comment)
    assert Comment.objects.get_comment() == comment


@pytest.mark.django_db
def test_get_comment(comment_factory, comment):
    comment_factory.create(comment=comment)
    assert Comment.objects.get_comment() == comment


@pytest.mark.django_db
def test_get_comment_when_none_exists():
    with pytest.raises(Comment.DoesNotExist):
        Comment.objects.get_comment()
