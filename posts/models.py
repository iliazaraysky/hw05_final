from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок группы',
                             help_text='Укажите заголовок группы')
    slug = models.SlugField(max_length=160, unique=True,
                            verbose_name='Slug (идентификатор)',
                            help_text='Slug это уникальная строка,'
                                      'понятная человеку')
    description = models.TextField(verbose_name='Описание',
                                   help_text='У группы должно быть описание')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Группы'


class Post(models.Model):
    text = models.TextField(verbose_name='Текст сообщения',
                            help_text=('Обязательное поле,'
                                       'не должно быть пустым'))
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True,
                               null=True, related_name='posts',
                               verbose_name='Автор',
                               help_text='Выберите имя автора')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, blank=True,
                              null=True, related_name='posts',
                              verbose_name='Группа',
                              help_text='Выберите название группы')
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments', verbose_name='Пост',
                             help_text='Под каким постом оставлен комментарий')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Автор комментария',
                               help_text='Автор отображается на сайте')
    text = models.TextField(verbose_name='Текст комментария',
                            help_text=('Обязательное поле,'
                                       'не должно быть пустым'))
    created = models.DateTimeField(verbose_name='Дата публикации',
                                   help_text='Дата публикации',
                                   auto_now_add=True)

    class Meta:
        ordering = ('-created',)
        verbose_name_plural = 'Комментарии к постам'

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='Пользователь подписан на')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="following", verbose_name="Автора")

    class Meta:
        constraints = (models.UniqueConstraint(fields=('user', 'author'),
                                               name='Пара уникальных значений')
                       )
        verbose_name_plural = 'Пользователи / Подписки'
