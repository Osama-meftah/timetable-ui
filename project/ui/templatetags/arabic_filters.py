from django import template

register = template.Library()

@register.filter
def arabic_level(name):
    mapping = {
        'first': 'الأول',
        'second': 'الثاني',
        'third': 'الثالث',
        'fourth': 'الرابع',
        'fifth': 'الخامس',
        'sixth': 'السادس',
        'seventh': 'السابع',
        'eighth': 'الثامن',
        'ninth': 'التاسع',
        'tenth': 'العاشر',
    }
    return mapping.get(name.lower(), name)
