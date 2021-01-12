from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from posts.models import Post, Group


User = get_user_model()


class ViewTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
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
    
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create(username='author')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
    
    def test_pages_uses_correct_template(self):
        """URL-адреса использует соответствующие шаблоны."""
        templates_pages_name={
            'index.html': reverse('index'),
            'group.html': reverse('group', kwargs=
            {'slug':'test-group'}),
            'new.html': reverse('new_post'),
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech')
        }
        for template, reverse_name in templates_pages_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test__page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('index'))
        expected = ViewTest.post
        form_field = response.context.get('page')[0]
        self.assertEqual(form_field, expected)

    def test_group_page_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('group', kwargs=
            {'slug':'test-group'}))
        expected = Group.objects.all()[0]
        form_field = response.context.get('group')
        self.assertEqual(form_field, expected)
    
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
    
    def test_new_post_with_group_shown_as_expected(self):
        """Сформированный пост отображается корректно
        на странице выбранной группы."""
        response = self.authorized_client.get(reverse('group', kwargs=
            {'slug':'test-group01'}))
        self.assertIsNone(response.context.get('post'))
   
    def test_edit_posts_show_correct_context(self):
        """Содержимое словаря context для страницы 
        редактирования поста."""
        username = ViewTest.user_author.username
        post_id = ViewTest.post.id
        response = self.authorized_client.get(
            reverse('post_edit', kwargs={
            'username': username,
            'post_id': post_id})
            )
        models_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in models_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
    
    def test_user_profile_show_correct_context(self):
        """Содержимое словаря context для страницы 
        профиля пользователя."""
        username = ViewTest.user_author.username
        response = self.authorized_client.get(
            reverse('profile', kwargs={
            'username': username})
            )
        expected = ViewTest.post
        form_field = response.context.get('page')[0]
        self.assertEqual(form_field, expected)

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
        form_field = response.context.get('post')
        self.assertEqual(form_field, expected)
