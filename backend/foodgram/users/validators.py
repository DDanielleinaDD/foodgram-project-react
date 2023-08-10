import re

from django.core.exceptions import ValidationError


def validate_username(value):
    '''Проверяем username на валидность знаков.'''
    pattern = r'^[\w.@+-]+$'
    if value.lower == 'me':
        raise ValidationError(
            'Username не может быть me.'
        )
    if re.match(pattern, value) is None:
        raise ValidationError(
            'Проверьте username на отсутствие запрещенных знаков'
        )
    return value
