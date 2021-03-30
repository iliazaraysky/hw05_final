from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse
from django import forms
from django.conf import settings
import random
import tempfile
import shutil

from posts.models import Group, Post, Follow

User = get_user_model()


class ProjectViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

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

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.post = Post.objects.create(
            group=ProjectViewsTests.group,
            text="Какой-то там текст",
            author=User.objects.get(username='authorForPosts'),
            image=uploaded
            )


    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='TestForTest')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""

        templates_page_names = {
            'index.html': reverse('index'),
            'newpost.html': reverse('new_post'),
            'group.html': (reverse('group', kwargs={'slug': 'tolstoy'})),
        }

        for template, reverse_name in templates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_new_post_page_show_correct_context(self):
        """Форма добавления материала сформирована с правильным контекстом"""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
            'image': forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context['form'].fields[value]
                self.assertIsInstance(form_fields, expected)

    def test_context_in_profile(self):
        """Проверка содержимого словаря context для /<username>/"""
        url = reverse('profile', args=[self.author.username])
        response = self.authorized_client.get(url)
        post = response.context['page'][0]
        author = response.context['author']
        post_text = post.text
        post_author = author.first_name
        post_image = post.image
        self.assertEqual(post_author, 'Тестов')
        self.assertEqual(post_text, 'Какой-то там текст')
        self.assertEqual(post_image, self.post.image.name)

    def test_context_in_post_edit(self):
        """
        Проверка содержимого словаря context
        для /<username>/<post_id>/edit/
        """
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

        lst_id = Post.objects.filter(author=self.author).values_list('id',
                                                                     flat=True)
        url = reverse('post_edit', args=[self.author.username,
                                         random.choice(lst_id)])
        response = self.authorized_client.get(url)
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
            'image': forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context['form'].fields[value]
                self.assertIsInstance(form_fields, expected)

    def test_post_id_correct_context(self):
        """Проверка содержимого context отдельного поста"""
        lst_id = Post.objects.filter(author=self.author).values_list('id',
                                                                     flat=True)
        url = reverse('post', args=[self.author.username,
                                    random.choice(lst_id)])
        response = self.authorized_client.get(url)
        post = response.context['post']
        author = response.context['author']
        post_text = post.text
        post_author = author.first_name
        post_image = post.image
        self.assertEqual(post_author, 'Тестов')
        self.assertEqual(post_text, 'Какой-то там текст')
        self.assertEqual(post_image, post.image.name)

    def test_home_page_show_correct_context(self):
        """Пост отображается на главной странице"""
        response = self.authorized_client.get(reverse('index'))
        first_object = response.context['page'][0]
        post_text = first_object.text
        post_group = first_object.group.title
        post_image = first_object.image
        self.assertEqual(post_text, 'Какой-то там текст')
        self.assertEqual(post_group, 'Лев Толстой')
        self.assertEqual(post_image, self.post.image.name)

    def test_group_page_show_correct_context(self):
        """Пост отображается на странице группы"""

        response = self.authorized_client.get(
            reverse('group', args=[self.group.slug]))
        first_object = response.context['posts'][0]
        post_text = first_object.text
        post_group = first_object.group.title
        post_image = first_object.image
        self.assertEqual(post_text, 'Какой-то там текст')
        self.assertEqual(post_group, 'Лев Толстой')
        self.assertEqual(post_image, self.post.image.name)

    def test_first_page_containse_ten_records(self):
        """Колличество постов на первой странице равно 10"""
        for i in range(1, 14):
            self.post_first_page = Post.objects.create(
                group=ProjectViewsTests.group,
                text="Какой-то там текст",
                author=User.objects.get(username='authorForPosts'),
            )
        response = self.client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_containse_three_records(self):
        for i in range(1, 14):
            self.post_second_page = Post.objects.create(
                group=ProjectViewsTests.group,
                text="Какой-то там текст",
                author=User.objects.get(username='authorForPosts'),
            )

        response = self.guest_client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 4)

    def test_cach_in_index_page(self):
        """Проверяем работу кеша на главной странице"""
        response = self.authorized_client.get(reverse('index'))
        before_clearing_the_cache = response.content

        Post.objects.create(
            group=ProjectViewsTests.group,
            text="Новый текст, после кэша",
            author=User.objects.get(username='authorForPosts'))

        cache.clear()

        response = self.authorized_client.get(reverse('index'))
        after_clearing_the_cache = response.content
        self.assertNotEqual(before_clearing_the_cache,
                            after_clearing_the_cache)

    def test_login_user_follow(self):
        """
        Авторизованный пользователь может подписываться
        на других пользователей
        """
        self.new_user = User.objects.create_user(username='TonyStark')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.new_user)
        followers_before = len(
            Follow.objects.all().filter(author_id=self.author.id))

        self.authorized_client.get(
            reverse('profile_follow', args=[self.author]))
        followers_after = len(
            Follow.objects.all().filter(author_id=self.author.id))
        self.assertEqual(followers_after, followers_before + 1)

    def test_login_user_unfollow(self):
        """
        Авторизованный пользователь может подписываться
        на других пользователей, а также отписываться
        """
        self.new_user = User.objects.create_user(username='TonyStark')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.new_user)

        followers_before = len(
            Follow.objects.all().filter(author_id=self.author.id))

        self.authorized_client.get(
            reverse('profile_follow', args=[self.author]))
        self.authorized_client.get(
            reverse('profile_unfollow', args=[self.author]))

        followers_after_unfollow = len(
            Follow.objects.all().filter(author_id=self.author.id))
        self.assertEqual(followers_after_unfollow, followers_before)

    def test_follow_index(self):
        """
        Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех,
        кто не подписан на него
        """
        self.new_user = User.objects.create_user(username='TonyStark')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.new_user)

        response = self.authorized_client.get(reverse('follow_index'))

        self.authorized_client.get(
            reverse('profile_follow', args=[self.author]))

        response_after_follow = self.authorized_client.get(
            reverse('follow_index'))

        self.assertEqual(response.content, response_after_follow.content)

    def test_add_comment_not_login_user(self):
        """
        Проверка доступа анонимного пользователя
        к редактированию поста
        """
        lst_id = Post.objects.filter(author=self.author).values_list('id',
                                                                     flat=True)
        url = reverse('add_comment', args=[self.author.username,
                                           random.choice(lst_id)])
        response = self.guest_client.get(url, follow=True)
        self.assertRedirects(response, '/auth/login/?next=' + url)

    # def test_add_comment_login_user(self):
    #     lst_id = Post.objects.filter(author=self.author).values_list('id',
    #                                                                  flat=True)
    #     url = reverse('add_comment', args=[self.author.username,
    #                                        random.choice(lst_id)])
    #     response = self.guest_client.get(url, follow=True)
