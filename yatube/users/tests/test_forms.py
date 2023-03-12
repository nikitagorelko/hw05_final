from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class CreationFormTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        User.objects.create_user(username='auth')

    def test_sign_up(self):
        """Проверят, что валидная форма создает нового пользователя."""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Test',
            'last_name': 'Form',
            'username': 'testuser',
            'email': 'testform@mail.ru',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }
        self.guest_client.post(
            reverse('users:signup'), data=form_data, follow=True
        )
        self.assertEqual(User.objects.count(), users_count + 1)
