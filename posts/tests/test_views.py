from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from itertools import islice

from posts.models import Post, Group


User = get_user_model()


class ViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create(username='VladOs')
        cls.group = Group.objects.create(            
            title='Группа для теста',
            slug='test-group',
            description='Группа для теста'
        )
        cls.group_01 = Group.objects.create(            
            title='Группа для теста 01',
            slug='test-group01',
            description='Группа01 для теста'
        )
        cls.post = Post.objects.create(
            text = 'Текст теста',
            author = cls.user_author,
            group = cls.group,
        )
        cls.post_01 = Post.objects.create(
            text = 'Текст теста01',
            author = cls.user_author,
            group = cls.group_01
        )
    
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create(username='author')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post_author = Client()
        self.post_author.force_login(ViewTest.user_author)
    
    def test_pages_uses_correct_template(self):
        """URL-адреса использует соответствующие шаблоны."""
        templates_pages_name={
            'index.html': reverse('index'),
            'group.html': reverse('group', kwargs=
            {'slug': ViewTest.group.slug}),
            'new.html': reverse('new_post'),
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech')
        }
        for template, reverse_name in templates_pages_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_main_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('index'))
        expected = ViewTest.post
        post_context = response.context.get('page')[0]
        self.assertEqual(post_context, expected)

    def test_group_page_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('group', kwargs=
            {'slug': ViewTest.group.slug}))
        expected = Group.objects.get(slug=ViewTest.group.slug)
        group_context = response.context.get('group')
        self.assertEqual(group_context, expected)
    
    def test_post_creation_page_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        models_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in models_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
    
    def test_new_post_with_group_shown_in_expected_group(self):
        """Сформированный пост отображается корректно
        на странице выбранной группы."""
        response = self.authorized_client.get(reverse('group', kwargs=
            {'slug': ViewTest.group_01.slug}))
        group_title = response.context.get('group')
        expected = ViewTest.post_01.group
        self.assertEqual(group_title, expected)

    def test_new_post_with_group_shown_in_main_page(self):
        """Сформированный пост с указанной группой
        отображается корректно на главной странице."""
        response = self.authorized_client.get(reverse('index'))
        index = response.context.get('page')[1].text
        expected = ViewTest.post_01.text
        self.assertEqual(index, expected)
   
    def test_edit_posts_show_correct_context(self):
        """Содержимое словаря context для страницы 
        редактирования поста."""
        username = ViewTest.user_author.username
        post_id = ViewTest.post.id
        response = self.post_author.get(
            reverse('post_edit', kwargs={
            'username': username,
            'post_id': post_id})
            )
        models_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        expected_author = ViewTest.post.author
        page_context_author = response.context.get('post').author
        for value, expected in models_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertEqual(page_context_author, expected_author)
    
    def test_user_profile_show_correct_context(self):
        """Содержимое словаря context для страницы 
        профиля пользователя."""
        username = ViewTest.user_author.username
        response = self.authorized_client.get(
            reverse('profile', kwargs={
            'username': username})
            )
        expected_post = ViewTest.post
        expected_author = ViewTest.post.author
        page_context = response.context.get('page')[0]
        page_context_author = response.context.get('post').author
        self.assertEqual(page_context, expected_post)
        self.assertEqual(page_context_author, expected_author)

    def test_one_post_show_correct_context(self):
        """Содержимое словаря context для страницы 
        отдельного поста."""
        username = ViewTest.user_author.username
        post_id = ViewTest.post.id
        response = self.authorized_client.get(
            reverse('post', kwargs={
            'username': username,
            'post_id': post_id})
            )
        expected = ViewTest.post
        post_context = response.context.get('post')
        self.assertEqual(post_context, expected)
    
    def test_paginator(self):
        """Проверка паджинатора на гл. странице."""
        batch_size = 20
        objs = (Post(author=ViewTest.user_author, text='Test %s' % i) for i in range(20))
        while True:
            batch = list(islice(objs, batch_size))
            if not batch:
                break
            Post.objects.bulk_create(batch, batch_size)
        response = self.guest_client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list), 12)
