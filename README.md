# Простая социальная сеть. Блоги.
Финальная часть проекта. В этот блок будет добавлена подписка на авторов, а также будет создана лента их постов
Помимо основного функционала, дописаны следующие блоки:
1. С помощью sorl-thumbnail выведены иллюстрации к постам
2. Написаны тесты:
    - на главную страницу
    - на страницу профайла
    - на страницу группы
    - на отдельную страницу поста
3. Создана система комментариев
4. Кэширование главной страницы
5. Тестирование кэша

## Инструкция по установке

Клонируем репозиторий

<code>git clone https://github.com/iliazaraysky/hw05_final.git</code>

Переходим в папку с проектом

<code>cd hw05_final/</code>

Устанавливаем отдельное виртуальное окружение для проекта

<code>python -m venv venv</code>

Активируем виртуальное окружение

<code>venv\Scripts\activate</code>

Устанавливаем модули необходимые для работы проекта

<code>pip install -r requirements.txt</code>

# Требования
Python 3.6 +

Работает под ОС Linux, Windows, macOS, BSD

# Ранние сборки проекта
1. [Сообщества. Блог](https://github.com/iliazaraysky/hw02_community)
2. [Формы для отправки и редактирования данных на сайте](https://github.com/iliazaraysky/hw03_forms)
3. [Тесты. Unittest в Django](https://github.com/iliazaraysky/hw04_tests)
