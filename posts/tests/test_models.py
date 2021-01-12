from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Post, Group


User = get_user_model()


class ModelsTest(TestCase):
    @classmethod
    def setUpClass(cls)-> None:
        super().setUpClass()
        cls.user_author = User.objects.create(username='VladOs')
        cls.group = Group.objects.create(
            title = 'Тестовое название группы',
            description = 'Тестовое описание группы',
            slug = 'test-group'
        )
        cls.post = Post.objects.create(
            text = 'Текст теста',
            author = cls.user_author,
            group = cls.group
        )
    
    def test_object_text_is_str_field(self):
        post = ModelsTest.post
        expected_object_text = post.text
        self.assertEqual(expected_object_text, str(post))
    
    def test_object_title_is_str_field(self):
        group = ModelsTest.group
        expected_object_title = group.title
        self.assertEqual(expected_object_title, str(group))
