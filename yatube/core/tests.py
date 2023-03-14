from django.test import TestCase
from yatube.settings import DEBUG


class CoreTests(TestCase):
    def test_404_page_uses_correct_template(self) -> None:
        """Проверяет, что страница 404 отдаёт кастомный шаблон."""
        if not DEBUG:
            response = self.client.get('/missing/')
            self.assertTemplateUsed(response, 'core/404.html')
