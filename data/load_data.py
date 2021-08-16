import csv
import os
import sys

import django

sys.path.append('../')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api_yamdb.settings")
django.setup()


def load_all_data(func):
    from api.models import (Category, Comment, Genre,
                            GenreTitle, Review, Title, User)

    func('genre.csv', Genre)
    print('\nЖанры загружены\n')

    func('category.csv', Category)
    print('\nКатегории загружены\n')

    func('titles.csv', Title)
    print('\nПроизведения загружены\n')

    func('genre_title.csv', GenreTitle)
    print('\nЖанры-Произведения\n')

    func('users.csv', User)
    print('\nПользователи загружены\n')

    func('users.csv', User)
    print('\nПользователи загружены\n')

    func('review.csv', Review)
    print('\nОтзывы загружены\n')

    func('comments.csv', Comment)
    print('\nКоментарии загружены\n')


@load_all_data
def load_table_from_csv(fname, model):
    from api.models import (Category, Genre, Title, User)

    file = open(fname, 'r', encoding='utf-8')
    reader = csv.DictReader(file, delimiter=',')
    for row in reader:
        if fname == 'titles.csv':
            row['category'] = Category.objects.get(id=row['category'])
        if fname == 'genre_title.csv':
            row['genre'] = Genre.objects.get(id=row['genre'])
            row['title'] = Title.objects.get(id=row['title'])
        if fname == 'review.csv':
            row['author'] = User.objects.get(id=row['author'])
        if fname == 'comments.csv':
            row['author'] = User.objects.get(id=row['author'])

        record = model(**row)
        record.save()
        print(f'{row}')
