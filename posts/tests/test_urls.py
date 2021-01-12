from django.contrib.auth import get_user_model

from django.test import TestCase, Client

from posts.models import Post, Group


User = get_user_model()


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user_author = User.objects.create(username='author')
        cls.group = Group.objects.create(            
            title='Группа для теста',
            slug='test-group',
            description='Группа для теста'
        )
        cls.post = Post.objects.create(
            text = 'Текст тестового поста',
            author = cls.user_author,
            group = cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create(username='VladOs')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
    
    def test_new_post_creation(self):
        """Доступ к страницам авториз. пользователям."""
        urls_pages_names = {
            '/new/': 200,
            f'/{self.user_author.username}/1/edit/': 200
        }
        for url, code in urls_pages_names.items():
            response = self.authorized_client .get(url)
            self.assertEqual(response.status_code, code)
    
    def test_urls_access_guest_client(self):
        """Доступ к страницам неавториз. пользователям."""
        urls_pages_names = {
            '/': 200,
            '/group/test-group/': 200,
            '/new/': 302,
            '/about/author/': 200,
            '/about/tech/': 200,
            f'/{self.user_author.username}/': 200,
            f'/{self.user_author.username}/1/': 200,
            f'/{self.user_author.username}/1/edit/': 302
        }
        for url, code in urls_pages_names.items():
            response = self.guest_client.get(url)
            self.assertEqual(response.status_code, code)

    def test_urls_uses_correct_template(self):
        """Тест вызова HTML шаблонов."""
        templates_url_names={
            'index.html': '/',
            'group.html': '/group/test-group/',
            'new.html': '/new/',
            'new.html':f'/{self.user_author.username}/1/edit/'
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
