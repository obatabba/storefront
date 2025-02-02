from django.core.exceptions import ValidationError


def validate_file_size(file):
    MAX_SIZE_KB = 500

    if file.size > MAX_SIZE_KB * 1024:
        raise ValidationError(f'Files cannot be larger than {MAX_SIZE_KB}KB!')