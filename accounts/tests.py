from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import UserProfile


class AuthenticationFlowTests(TestCase):
    def test_signup_creates_user_profile_with_mobile_number(self):
        response = self.client.post(
            reverse('register'),
            {
                'name': 'Ava Brown',
                'username': 'ava',
                'email': 'ava@example.com',
                'mobile_number': '9876543210',
                'password': 'StrongPass123',
                'confirm_password': 'StrongPass123',
            },
        )

        self.assertEqual(response.status_code, 302)
        user = get_user_model().objects.get(username='ava')
        self.assertEqual(user.email, 'ava@example.com')
        self.assertEqual(user.first_name, 'Ava')
        self.assertTrue(UserProfile.objects.filter(user=user, mobile_number='9876543210').exists())

    def test_login_with_email_redirects_to_home(self):
        user = get_user_model().objects.create_user(
            username='demo',
            email='demo@example.com',
            password='StrongPass123',
        )
        response = self.client.post(
            reverse('login'),
            {'username': 'demo@example.com', 'password': 'StrongPass123'},
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        self.assertIn('_auth_user_id', self.client.session)
