from django.core.exceptions import ValidationError


def validate_file_size(file):
    MAX_SIZE_KB = 50

    if file.size * 1024 > MAX_SIZE_KB:
        raise ValidationError(f'Files cannot be larger than {MAX_SIZE_KB}KB!')