FIELDS_TO_ORDER = [
    'imdb_rating',
    'title.raw',
    'genres.id'
]


def validate_order_field(field: str):
    reverse = ['-' + item for item in FIELDS_TO_ORDER]
    all_fields = FIELDS_TO_ORDER + reverse
    if all_fields.count(field) > 0:
        return True
    else:
        return False


def parseOrderField(field: str):
    if field[0] == "-":
        return 'desc', field[1:]
    else:
        return 'asc', field
