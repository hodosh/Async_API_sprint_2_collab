film_data = {
    'key': '111111-000000-000000-redis',
    'data': {
        'id': '111111-000000-000000-redis',
        'imdb_rating': 8.6,
        'title': 'Star Czars II',
        'description': 'bla-bla-bla',
        'genres': [
            {
                'id': '222222-000000-000000-000000',
                'name': 'Reality-TV',
            },
        ],
        'directors': [],
        'actors': [
            {
                'id': '333333-000000-000000-000000',
                'name': 'Dominic C. Skinner',
            },
        ],
        'writers': [],
    },
}

person_data = {
    'key': '222222-000000-000000-redis',
    'data': {
        'id': '222222-000000-000000-redis',
        'full_name': 'George Lucas Jr II',
        'film_roles': [
            {
                'id': 'e5a21648-59b1-4672-ac3b-867bcd64b6ea',
                'name': 'writer',
            },
            {
                'id': 'c8f57f93-b02a-40d4-ba55-9600cceddd7e',
                'name': 'director',
            },
        ],
    },
}

genre_data = {
    'key': '333333-000000-000000-redis',
    'data': {
        'id': '333333-000000-000000-redis',
        'name': 'Action',
        'film_ids': [
            {
                'id': 'e5a21648-59b1-4672-ac3b-867bcd64b6ea',
            },
            {
                'id': 'c8f57f93-b02a-40d4-ba55-9600cceddd7e',
            },
        ],
    },
}
