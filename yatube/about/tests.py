from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse


class StaticPagesURLTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.urls = {
            'author': reverse('about:author'),
            'tech': reverse('about:tech'),
        }

    def test_http_statuses(self) -> None:
        """Проверяет доступность URL-адреса."""
        httpstatuses = (
            (self.urls.get('author'), HTTPStatus.OK, self.client),
            (self.urls.get('tech'), HTTPStatus.OK, self.client),
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
                self.urls.get('author'),
                'about/author.html',
                self.client,
            ),
            (
                self.urls.get('tech'),
                'about/tech.html',
                self.client,
            ),
        )
        for template in templates:
            with self.subTest(template=template):
                self.assertTemplateUsed(
                    template[2].get(template[0]), template[1]
                )

    def test_pages_uses_correct_template(self) -> None:
        """Проверяет, что view-класс использует соответствующий шаблон."""
        templates_pages_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertTemplateUsed(response, template)
