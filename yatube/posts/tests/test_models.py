import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from mixer.backend.django import mixer

from ..models import Group, Post

TEMP_MEDIA_ROOT_MODELS = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT_MODELS)
class PostModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = mixer.blend(User, username='auth')
        cls.post = mixer.blend(Post, author=cls.user)

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT_MODELS, ignore_errors=True)

    def test_post_model_have_correct_string_representation(self) -> None:
        """Проверяет, правильно ли отображается значение поля __str__
        в объектах модели Group"""
        self.assertEqual(self.post.text[:15], str(self.post))


class GroupModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.group = mixer.blend(Group)

    def test_group_model_have_correct_string_representation(self) -> None:
        """Проверяет, правильно ли отображается значение поля __str__
        в объектах модели Group"""
        self.assertEqual(self.group.title, str(self.group))
