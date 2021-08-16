from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

YEAR_VALIDATION_ERROR = 'Нельзя добавить произведение из будущего'
SCORE_VALIDATION_ERROR = 'Оценка должна быть от 1 до 10'


class User(AbstractUser):

    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'

    ROLE = (
        (ADMIN, 'admin'),
        (MODERATOR, 'moderator'),
        (USER, 'user'),
    )

    bio = models.TextField(
        blank=True,
        verbose_name='О себе'
    )
    email = models.EmailField(
        unique=True,
        verbose_name='Адрес электронной почты'
    )
    role = models.CharField(
        max_length=15,
        choices=ROLE,
        default=USER,
    )

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return (self.role == self.ADMIN or self.is_staff
                or self.is_superuser)

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название категории',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Уникальный идентификатор категории',
    )

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'категирия'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название жанра',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Уникальный идентификатор жанра',
    )

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'жанр'
        verbose_name_plural = 'жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название произведения',
    )
    year = models.PositiveSmallIntegerField(
        verbose_name='Год создания',
        validators=[
            MaxValueValidator(
                datetime.now().year,
                message=YEAR_VALIDATION_ERROR
            )
        ]
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        blank=True,
        null=True,
        verbose_name='Категория',
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True,
        null=True,
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        through_fields=['title', 'genre']
    )

    class Meta:
        ordering = ('-pk', 'name',)
        verbose_name = 'произведение'
        verbose_name_plural = 'произведения'

    def __str__(self):
        return (f'{self.name} '
                f'({self.category})')


class GenreTitle(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='Жанр',
    )

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'Привязка жанров'
        verbose_name_plural = 'Привязки жанров'

    def __str__(self):
        return (f'({self.title}->{self.genre})')


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        blank=True,
        on_delete=models.CASCADE,
        null=False,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField(
        verbose_name='Текст',
        help_text='Заполните поле.',
    )

    author = models.ForeignKey(
        User,
        blank=True,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        null=False,
        related_name='reviews',
    )
    score = models.PositiveSmallIntegerField(
        help_text='Введите от 1 до 10',
        default=10,
        verbose_name='Оценка',
        validators=(MinValueValidator(1, message=SCORE_VALIDATION_ERROR),
                    MaxValueValidator(10, message=SCORE_VALIDATION_ERROR))
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True,
    )

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ('-pub_date',)
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(fields=['author', 'title'],
                                    name='title_review')
        ]


class Comment(models.Model):
    text = models.TextField(
        null=False,
        verbose_name='Текст',
        help_text='Заполните поле.',
    )
    author = models.ForeignKey(
        User,
        blank=False,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        null=False,
        related_name='comments',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True,
    )
    review = models.ForeignKey(
        Review,
        blank=False,
        verbose_name='Отзыв',
        on_delete=models.CASCADE,
        null=False,
        related_name='comments',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name_plural = 'Коментарии'
