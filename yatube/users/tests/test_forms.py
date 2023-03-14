from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from faker import Faker

User = get_user_model()
fake = Faker()


class CreationFormTests(TestCase):
    def test_sign_up(self) -> None:
        """Проверят, что валидная форма создает нового пользователя."""
        data = {
            'first_name': fake.pystr(),
            'last_name': fake.pystr(),
            'username': fake.pystr(),
            'email': fake.email(),
            'password1': 'testpassword',
            'password2': 'testpassword',
        }
        self.client.post(reverse('users:signup'), data=data, follow=True)
        self.assertEqual(User.objects.count(), 1)
