base_genre_data = {'id': '333333-000000-000000-000000', 'name': 'Action', 'description': None,
                   'film_ids': [{'id': '111111-000000-000000-000001'}, {'id': '111111-000000-000000-000002'}]}

film_data = {'id': '111111-333333-000000-000000', 'imdb_rating': 8.6, 'title': 'Star Czars',
             'description': 'bla-bla-bla', 'genres': [{'id': '333333-000000-000000-000001', 'name': 'Reality-TV'}],
             'directors': [], 'actors': [], 'writers': []}

genre_with_film_details = {'id': '333333-000000-000000-000001', 'name': 'Reality-TV', 'description': None,
                           'film_ids': [{'id': '111111-333333-000000-000000'}]}

genre_without_film_details = {'id': '333333-000000-000000-000002', 'name': 'Reality-TV', 'description': None,
                              'film_ids': []}
