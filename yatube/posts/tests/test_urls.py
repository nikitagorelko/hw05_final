import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.views import redirect_to_login
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from mixer.backend.django import mixer

from ..models import Group, Post

TEMP_MEDIA_ROOT_URLS = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT_URLS)
class PostUrlTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = mixer.blend(User, username='auth')
        cls.group = mixer.blend(Group)
        cls.post = mixer.blend(Post, author=cls.user, group=cls.group)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.urls = {
            'post_create': reverse('posts:post_create'),
            'group_list': reverse(
                'posts:group_list', kwargs={'slug': cls.group.slug}
            ),
            'index': reverse('posts:index'),
            'post_detail': reverse(
                'posts:post_detail', kwargs={'post_id': cls.post.id}
            ),
            'post_edit': reverse(
                'posts:post_edit', kwargs={'post_id': cls.post.id}
            ),
            'profile': reverse(
                'posts:profile', kwargs={'username': cls.user.username}
            ),
            'add_comment': reverse(
                'posts:add_comment', kwargs={'post_id': cls.post.id}
            ),
            'missing': '/missing/',
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT_URLS, ignore_errors=True)

    def test_http_statuses(self) -> None:
        """Проверяет доступность URL-адреса."""
        httpstatuses = (
            (self.urls.get('post_create'), HTTPStatus.FOUND, self.client),
            (
                self.urls.get('post_create'),
                HTTPStatus.OK,
                self.authorized_client,
            ),
            (self.urls.get('group_list'), HTTPStatus.OK, self.client),
            (self.urls.get('index'), HTTPStatus.OK, self.client),
            (self.urls.get('post_detail'), HTTPStatus.OK, self.client),
            (self.urls.get('post_edit'), HTTPStatus.FOUND, self.client),
            (
                self.urls.get('post_edit'),
                HTTPStatus.OK,
                self.authorized_client,
            ),
            (self.urls.get('profile'), HTTPStatus.OK, self.client),
            (
                self.urls.get('add_comment'),
                HTTPStatus.FOUND,
                self.authorized_client,
            ),
            (self.urls.get('missing'), HTTPStatus.NOT_FOUND, self.client),
        )
        for status in httpstatuses:
            with self.subTest(status=status):
                self.assertEqual(
                    status[2].get(status[0]).status_code, status[1]
                )

    def test_templates(self) -> None:
        cache.clear()
        """Проверяет, что URL-адрес использует соответствующий шаблон."""
        templates = (
            (
                self.urls.get('post_create'),
                'posts/create_post.html',
                self.authorized_client,
            ),
            (
                self.urls.get('group_list'),
                'posts/group_list.html',
                self.client,
            ),
            (self.urls.get('index'), 'posts/index.html', self.client),
            (
                self.urls.get('post_detail'),
                'posts/post_detail.html',
                self.client,
            ),
            (
                self.urls.get('post_edit'),
                'posts/create_post.html',
                self.authorized_client,
            ),
            (self.urls.get('profile'), 'posts/profile.html', self.client),
        )
        for template in templates:
            with self.subTest(template=template):
                self.assertTemplateUsed(
                    template[2].get(template[0]), template[1]
                )

    def test_redirects(self) -> None:
        """Проверяет, что страница по URL-адресу
        перенаправляет пользователя."""
        user = mixer.blend(User, username='auth1')
        new_authorized_client = Client()
        new_authorized_client.force_login(user)
        redirects = (
            (
                self.urls.get('post_create'),
                redirect_to_login(
                    reverse('posts:post_create'),
                    login_url=reverse('users:login'),
                ).url,
                self.client,
            ),
            (
                self.urls.get('post_edit'),
                redirect_to_login(
                    reverse(
                        'posts:post_edit', kwargs={'post_id': self.post.id}
                    ),
                    login_url=reverse('users:login'),
                ).url,
                self.client,
            ),
            (
                self.urls.get('post_edit'),
                reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
                new_authorized_client,
            ),
            (
                self.urls.get('add_comment'),
                redirect_to_login(
                    reverse(
                        'posts:add_comment', kwargs={'post_id': self.post.id}
                    ),
                    login_url=reverse('users:login'),
                ).url,
                self.client,
            ),
            (
                self.urls.get('add_comment'),
                reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
                self.authorized_client,
            ),
        )
        for redirect in redirects:
            with self.subTest(redirect=redirect):
                self.assertRedirects(redirect[2].get(redirect[0]), redirect[1])
