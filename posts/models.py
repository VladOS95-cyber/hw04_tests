from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """Модель сообщества куда буду попадать публикации
    в зависимости от тематики. Блогер будет иметь возможность
    самостоятельно выбрать группу, но создать группу
    смогут только админы. Модель имеет свойства:
    title(имя), адрес(slug) и описание(description).
    """
    title = models.CharField(
        verbose_name='Название группы',
        max_length=200,
        help_text = 'Напишите название группы'
        )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=50, 
        unique=True,
        help_text ='Укажите адрес для страницы задачи.'
        )
    description = models.TextField(
        verbose_name='Описание',
        help_text = 'Добавьте описание группы'
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    """Модель публикации, содержащая
    текст к публикации, дату, имя автора и
    ссылку на модель Group.
    """
    text = models.TextField(verbose_name='Текст поста', 
    help_text = 'Введите текст поста для публикации.')
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации', 
        auto_now_add=True,
        help_text = 'Дата добавляется автоматически'
        )
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name='Имя автора',
        related_name='posts',
        help_text = 'Имя автора добавляется автоматически'
    )
    group = models.ForeignKey(
        Group, on_delete=models.SET_NULL, 
        verbose_name='Группа',
        help_text = 'Выберите группу',
        blank=True, null=True,
        related_name='posts'
    )

    class Meta:
        """Класс для сортировки по датам."""
        ordering = ('-pub_date',)
    
    def __str__(self):
        return self.text[:15]
