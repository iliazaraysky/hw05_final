from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus
import random
from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
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

        for i in range(1, 5):
            cls.post = Post.objects.create(
                group=StaticURLTests.group,
                text='Какой-то там текст',
                author=User.objects.get(username='authorForPosts')
            )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='testfortest')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_comment_url_response(self):
        """Проверка доступности адреса для добавления комментария"""
        first_id = Post.objects.filter(author=self.author).first()
        response = self.guest_client.get(reverse('add_comment', args=[self.author.username, first_id.id]), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_follow_url_response(self):
        """Проверка доступности адреса Following пользователя"""
        response_login_user = self.authorized_client.get(reverse('profile_follow', args=[self.author]), follow=True)
        response_not_login_user = self.guest_client.get(reverse('profile_follow', args=[self.author]), follow=True)
        self.assertEqual(response_login_user.status_code, HTTPStatus.OK)
        self.assertEqual(response_not_login_user.status_code, HTTPStatus.OK)

    def test_unfollow_url_response(self):
        """Проверка доступности адреса Unfollowing пользователя"""
        response_login_user = self.authorized_client.get(reverse('profile_unfollow', args=[self.author]), follow=True)
        response_not_login_user = self.guest_client.get(reverse('profile_unfollow', args=[self.author]), follow=True)
        self.assertEqual(response_login_user.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(response_not_login_user.status_code, HTTPStatus.OK)

    def test_urls_list(self):
        """
        Тестирование по списку, для анонимного пользователя,
        список URL, где ответ должен быть равен 200
        """

        url_list = [reverse('index'), reverse('group', args=[self.group.slug])]
        for test_url in url_list:
            response = self.guest_client.get(test_url)
            self.assertEqual(response.status_code, 200)

    def test_response_anon_username_url(self):
        """
        Проверка доступности анонимным пользователем,
        страницы профиля пользователя
        """

        url = reverse('profile', args=[self.user.username])
        response = self.guest_client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_response_anon_username_post_url(self):
        """
        Проверка доступности анонимным пользователем,
        страницы с постом автора
        """

        total_number_of_id = len(
            Post.objects.filter(author=self.author).values_list('id',
                                                                flat=True))
        url = reverse('post', args=[self.user.username,
                                    random.randint(1, total_number_of_id)])
        response = self.guest_client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_redirect_anon_username_edit_post_url(self):
        """
        Проверка редиректа анонимного пользователя, при обращении
        к странице редактирования поста
        """

        total_number_of_id = len(
            Post.objects.filter(author=self.author).values_list('id',
                                                                flat=True))
        url = reverse('post_edit',
                      args=[self.user.username, total_number_of_id])
        response = self.guest_client.get(url)
        self.assertRedirects(response, '/auth/login/?next=' + url)

    def test_redirect_author_username_edit_post_url(self):
        """
        Проверка доступности страницы редактирования поста, при обращении
        автора
        """

        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        total_number_of_id = len(
            Post.objects.filter(author=self.author).values_list('id',
                                                                flat=True))
        url = reverse('post_edit',
                      args=[self.user.username, total_number_of_id])
        response = self.authorized_client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_redirect_not_author_username_edit_post_url(self):
        """
        Проверка редиректа при обращении к странице редактирования поста,
        авторизированным пользователем, не автором
        """

        total_number_of_id = len(
            Post.objects.filter(author=self.author).values_list('id',
                                                                flat=True))
        url = reverse('post_edit',
                      args=[self.user.username, total_number_of_id])
        response = self.authorized_client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_new_page_not_login_user(self):
        """Страница доступна авторизированному пользователю"""

        response = self.guest_client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_group_slug_response_not_login_user(self):
        """Проверка доступности созданной группы для всех пользователей"""

        response = self.guest_client.get(
            reverse('group', args=[self.group.slug]))
        self.assertEqual(response.status_code, 200)

    def test_new_page_not_login_user(self):
        """
        Страница создания нового поста,
        перенаправляет анонимного пользователя
        """

        response = self.guest_client.get(reverse('new_post'))
        self.assertEqual(response.status_code, 302)

    def test_new_page_login_user(self):
        """Главная страница доступна авторизированному пользователю"""

        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_group_slug_response_login_user(self):
        """
        Проверка доступности созданной группы
        для авторизированных пользователей
        """

        response = self.authorized_client.get(
            reverse('group', args=[self.group.slug]))
        self.assertEqual(response.status_code, 200)

    def test_new_page_login_user(self):
        """Страница доступна авторизированному пользователю"""

        response = self.authorized_client.get(reverse('new_post'))
        self.assertEqual(response.status_code, 200)

    def test_new_page_not_login_user_redirect(self):
        """Страница перенаправляет анонимного пользователя"""

        response = self.guest_client.get(reverse('new_post'), follow=True)
        self.assertRedirects(response, '/auth/login/?next=/new')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""

        template_url_names = {
            'index.html': reverse('index'),
            'group.html': reverse('group', args=[self.group.slug]),
            'newpost.html': reverse('new_post'),
        }
        for template, reverse_name in template_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_for_edit_post(self):
        """
        Проверка. Какой шаблон вызывается при обращении к странице
        редактирования поста
        """

        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        total_number_of_id = len(
            Post.objects.filter(author=self.author).values_list('id',
                                                                flat=True))
        url = reverse('post_edit',
                      args=[self.user.username, total_number_of_id])
        template_url_names = {'newpost.html': url}

        for template, reverse_name in template_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_about_and_tech_exist_all_users(self):
        """
        URL-адреса (/about/author/ и /about/tech/)
        доступны любому пользователю
        """
        urls_exist = [reverse('about:author'), reverse('about:tech')]

        for exist in urls_exist:
            with self.subTest():
                response = self.authorized_client.get(exist)
                self.assertEqual(response.status_code, 200)

    def test_404_response_code(self):
        """
        Если страница не найдена на сайте, возвращает код ответа 404
        """
        list_of_id = Post.objects.filter(
            author=self.author).values_list('id',
                                            flat=True)
        non_existent_post = list_of_id[0] - list_of_id[0]
        url = reverse('post', args=[self.user.username, non_existent_post])
        response = self.guest_client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)
