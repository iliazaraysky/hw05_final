# Generated by Django 2.2.6 on 2021-03-10 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_auto_20210310_1615'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(help_text='Slug это уникальная строка, понятная человеку', max_length=160, unique=True, verbose_name='Slug (идентификатор)'),
        ),
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(help_text='Обязательное поле, не должно быть пустым', verbose_name='Текст сообщения'),
        ),
    ]
