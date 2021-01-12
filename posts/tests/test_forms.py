import os
from posts.views import group_posts
import shutil
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django import forms

from posts.models import Post, Group


User = get_user_model()


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
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
        self.user = User.objects.create(username='author')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

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
        self.assertRedirects(response, '/')
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(text='Тестовый текст').exists())
    
    def test_post_edit(self):
        """Проверка редактирования поста."""
        username = PostFormTest.user_author.username
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
        self.assertNotEqual(Post.objects.first().text, form_data['text'])
        self.assertNotEqual(Post.objects.count(), post_count + 1)
