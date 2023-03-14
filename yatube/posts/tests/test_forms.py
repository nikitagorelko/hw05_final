import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from faker import Faker
from mixer.backend.django import mixer

from ..models import Comment, Group, Post

TEMP_MEDIA_ROOT_FORMS = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()
fake = Faker()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT_FORMS)
class PostFormTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = mixer.blend(User, username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT_FORMS, ignore_errors=True)

    def test_create_post(self) -> None:
        """Проверяет, что валидная форма создает запись в Posts."""
        data = {
            'text': fake.pystr(),
        }
        self.authorized_client.post(
            reverse('posts:post_create'), data=data, follow=True
        )
        self.assertEqual(Post.objects.count(), 1)

    def test_edit_post(self) -> None:
        """Проверяет, что при отправке валидной формы
        со страницы редактирования поста,
        происходит изменение поста в базе данных."""
        groups = mixer.cycle(2).blend(Group)
        post = mixer.blend(Post, author=self.user, group=groups[0])
        data = {'text': fake.pystr(), 'group': groups[1].id}
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=data,
            follow=True,
        )
        self.assertEqual(
            Post.objects.get(author=self.user).text, data.get('text')
        )
        self.assertEqual(
            Post.objects.get(author=self.user).group.id, data.get('group')
        )

    def test_anonym_create_post(self) -> None:
        """Проверяет, что анонимный пользователь не создает запись в Posts."""
        data = {
            'text': fake.pystr(),
        }
        self.client.post(reverse('posts:post_create'), data=data, follow=True)
        self.assertEqual(Post.objects.count(), 0)

    def test_anonym_edit_post(self) -> None:
        """Проверяет, что анонимный пользователь
        не может редактировать пост."""
        groups = mixer.cycle(2).blend(Group)
        post = mixer.blend(Post, author=self.user, group=groups[0])
        data = {'text': fake.pystr(), 'group': groups[1].id}
        self.client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=data,
            follow=True,
        )
        self.assertNotEqual(
            Post.objects.get(author=self.user).text, data.get('text')
        )
        self.assertNotEqual(
            Post.objects.get(author=self.user).group.id, data.get('group')
        )

    def test_not_auhtor_edit_post(self) -> None:
        """Проверяет, что пользователь, не являющийся автором,
        не может редактировать пост."""
        user = mixer.blend(User, username='auth1')
        new_authorized_client = Client()
        new_authorized_client.force_login(user)
        groups = mixer.cycle(2).blend(Group)
        post = mixer.blend(Post, author=self.user, group=groups[0])
        data = {'text': fake.pystr(), 'group': groups[1].id}
        new_authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=data,
            follow=True,
        )
        self.assertNotEqual(
            Post.objects.get(author=self.user).text, data.get('text')
        )
        self.assertNotEqual(
            Post.objects.get(author=self.user).group.id, data.get('group')
        )

    def test_create_post_with_image(self) -> None:
        """Проверяет, что при отправке поста с картинкой через форму PostForm
        создаётся запись в базе данных."""
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif', content=small_gif, content_type='image/gif'
        )
        data = {
            'text': fake.pystr(),
            'image': uploaded,
        }
        self.authorized_client.post(
            reverse('posts:post_create'), data=data, follow=True
        )
        self.assertEqual(Post.objects.count(), 1)

    def test_anonym_comment_post(self) -> None:
        """Проверяет, что анонимный пользователь
        не может комментировать пост."""
        post = mixer.blend(Post, author=self.user)
        data = {
            'text': fake.pystr(),
        }
        self.client.post(
            reverse('posts:add_comment', kwargs={'post_id': post.id}),
            data=data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), 0)
