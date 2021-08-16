from django_filters import rest_framework as rest_filters

from api.models import Title


class TitleFilter(rest_filters.FilterSet):
    genre = rest_filters.CharFilter(field_name='genre__slug',
                                    lookup_expr='exact')
    category = rest_filters.CharFilter(field_name='category__slug',
                                       lookup_expr='exact')
    year = rest_filters.NumberFilter(field_name='year', lookup_expr='exact')
    name = rest_filters.CharFilter(field_name='name', lookup_expr='contains')

    class Meta:
        model = Title
        fields = ['genre', 'category', 'year', 'name']
