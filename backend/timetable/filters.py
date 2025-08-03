# filters.py
import django_filters
from .models import Lecture,Subject

class LectureFilter(django_filters.FilterSet):
    program = django_filters.NumberFilter(field_name='fk_distribution__fk_group__fk_level__fk_program__id', lookup_expr='exact')

    class Meta:
        model = Lecture
        fields = ['program']

class SubjectFilter(django_filters.FilterSet):
    term = django_filters.CharFilter(field_name='term', lookup_expr='icontains')

    class Meta:
        model = Subject
        fields = ['term']
