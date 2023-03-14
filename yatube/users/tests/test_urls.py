from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.views import redirect_to_login
from django.test import Client, TestCase
from django.urls import reverse
from mixer.backend.django import mixer

User = get_user_model()


class UsersUrlTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = mixer.blend(User, username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.urls = {
            'sign_up': reverse('users:signup'),
            'login': reverse('users:login'),
            'password_change': reverse('users:password_change'),
            'password_change_done': reverse('users:password_change_done'),
            'password_reset': reverse('users:password_reset'),
            'password_reset_done': reverse('users:password_reset_done'),
            'password_reset_complete': reverse(
                'users:password_reset_complete'
            ),
            'logout': reverse('users:logout'),
        }

    def test_http_statuses(self) -> None:
        """Проверяет доступность URL-адреса."""
        httpstatuses = (
            (self.urls.get('sign_up'), HTTPStatus.OK, self.client),
            (self.urls.get('login'), HTTPStatus.OK, self.client),
            (self.urls.get('password_change'), HTTPStatus.FOUND, self.client),
            (
                self.urls.get('password_change'),
                HTTPStatus.OK,
                self.authorized_client,
            ),
            (
                self.urls.get('password_change_done'),
                HTTPStatus.FOUND,
                self.client,
            ),
            (
                self.urls.get('password_change_done'),
                HTTPStatus.OK,
                self.authorized_client,
            ),
            (self.urls.get('password_reset'), HTTPStatus.OK, self.client),
            (self.urls.get('password_reset_done'), HTTPStatus.OK, self.client),
            (
                self.urls.get('password_reset_complete'),
                HTTPStatus.OK,
                self.client,
            ),
            (self.urls.get('logout'), HTTPStatus.OK, self.client),
        )
        for status in httpstatuses:
            with self.subTest(status=status):
                self.assertEqual(
                    status[2].get(status[0]).status_code, status[1]
                )

    def test_templates(self) -> None:
        """Проверяет, что URL-адрес использует соответствующий шаблон."""
        templates = (
            (
                self.urls.get('sign_up'),
                'users/signup.html',
                self.client,
            ),
            (
                self.urls.get('login'),
                'users/login.html',
                self.client,
            ),
            (
                self.urls.get('password_change'),
                'users/password_change_form.html',
                self.authorized_client,
            ),
            (
                self.urls.get('password_change_done'),
                'users/password_change_done.html',
                self.authorized_client,
            ),
            (
                self.urls.get('password_reset'),
                'users/password_reset_form.html',
                self.client,
            ),
            (
                self.urls.get('password_reset_done'),
                'users/password_reset_done.html',
                self.client,
            ),
            (
                self.urls.get('password_reset_complete'),
                'users/password_reset_complete.html',
                self.client,
            ),
            (
                self.urls.get('logout'),
                'users/logged_out.html',
                self.client,
            ),
        )
        for template in templates:
            with self.subTest(template=template):
                self.assertTemplateUsed(
                    template[2].get(template[0]), template[1]
                )

    def test_redirects(self) -> None:
        """Проверяет, что страница по URL-адресу
        перенаправляет пользователя."""
        redirects = (
            (
                self.urls.get('password_change'),
                redirect_to_login(
                    reverse('users:password_change'),
                    login_url=reverse('users:login'),
                ).url,
                self.client,
            ),
            (
                self.urls.get('password_change_done'),
                redirect_to_login(
                    reverse('users:password_change_done'),
                    login_url=reverse('users:login'),
                ).url,
                self.client,
            ),
        )
        for redirect in redirects:
            with self.subTest(redirect=redirect):
                self.assertRedirects(redirect[2].get(redirect[0]), redirect[1])
