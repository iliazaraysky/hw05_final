from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post

import random

User = get_user_model()


class TestCreateForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Лев Толстой',
            slug='tolstoy',
            description='Группа Льва Толстого',
        )

        cls.author = User.objects.create_user(
            username='authorForPosts',
            first_name='Тестов',
            last_name='Теcтовский',
            email='testuser@yatube.ru'
        )

        cls.post = Post.objects.create(
            group=TestCreateForm.group,
            text="Какой-то там текст",
            author=User.objects.get(username='authorForPosts'),
        )

        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='TestForTest')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_form_create(self):
        """Проверка создания нового поста, авторизированным пользователем"""
        post_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'Отправить текст',
        }
        response = self.authorized_client.post(reverse('new_post'),
                                               data=form_data,
                                               follow=True)
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(
            text='Отправить текст',
            group=TestCreateForm.group).exists())

    def test_form_update(self):
        """
        Проверка редактирования поста через форму на странице
        """
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        url = reverse('post_edit', args=[self.author.username, 1])
        self.authorized_client.get(url)
        form_data = {
            'group': self.group.id,
            'text': 'Обновленный текст',
        }
        self.authorized_client.post(
            reverse('post_edit', args=[self.author.username, 1]),
            data=form_data, follow=True)

        self.assertTrue(Post.objects.filter(
            text='Обновленный текст',
            group=TestCreateForm.group).exists())

    def test_add_comment_login_user(self):
        self.new_user = User.objects.create_user(username='TonyStark')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.new_user)

        lst_id = Post.objects.filter(author=self.author).values_list('id',
                                                                     flat=True)
        random_url_data = random.choice(lst_id)
        form_data = {
            'text': 'Полностью разделяю позицию автора. Отличная работа!'
                    'Хорошо написано. Я бы также написал',
        }

        self.authorized_client.post(reverse('add_comment',
                                            args=[self.author.username,
                                                  random_url_data]),
                                    data=form_data, follow=True)
        response = self.authorized_client.get(
            reverse('post', args=[self.author.username, random_url_data]))
        last_comments = response.context['comments'][0]
        self.assertEqual(form_data['text'], str(last_comments))
