from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from posts.models import Post, Group


User = get_user_model()


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create(username='VladOs')
        cls.group = Group.objects.create(            
            title='Группа для теста',
            slug='test-group',
            description='Группа для теста'
        )
        cls.post = Post.objects.create(
            text = 'Текст теста',
            author = cls.user_author,
            group = cls.group,
        )
    
    
    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTest.user_author)

    def test_new_post_creation(self):
        """Проверка создания нового поста."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст'
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
            )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(text='Тестовый текст').exists())
    
    def test_post_edit(self):
        """Проверка редактирования поста."""
        username = self.user_author.username
        post_id = PostFormTest.post.id
        post_count = Post.objects.count()
        form_data = {
            'text': 'Новый тестовый текст'
        }
        self.authorized_client.post(
            reverse('post_edit', kwargs={
            'username': username,
            'post_id': post_id}),
            data=form_data,
            follow=True
            )
        self.assertNotEqual(Post.objects.filter(text='Тестовый текст'), form_data['text'])
        self.assertEqual(Post.objects.count(), post_count)
