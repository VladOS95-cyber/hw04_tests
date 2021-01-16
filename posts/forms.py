from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    """Класс для создания новой публикации пользователем."""
    class Meta:
        model = Post
        fields = ('group', 'text')
