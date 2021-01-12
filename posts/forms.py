from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    """Класс для создания новой публикации пользователем."""
    class Meta:
        model = Post
        fields = ('group', 'text')
        labels = {
            'group': 'Группа',
            'text': 'Текст'
        }
        help_text = {
            'group':'Выберите группу из списка. '
            'Это необязательное поле.',
            'text': 'Напишите текст публикации. '
            'Это поле обязательное.'
        }
