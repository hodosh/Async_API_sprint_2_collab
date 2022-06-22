from setup_logging import *
from transform import Transform

logger = get_logger()


class TransformMovies(Transform):
    def transform(self, data_table, augment_tables):
        processed_data = []
        for item in data_table:
            (id_, modified, title, description, rating) = item

            genres_list = self.get_plain_list(augment_tables['genres'][id_])
            actors_names_list = self.get_plain_list(augment_tables['actors'][id_])
            writers_names_list = self.get_plain_list(augment_tables['writers'][id_])
            director_list = self.get_plain_list(augment_tables['directors'][id_])

            genres_full_list = self.get_dict_list_2col(augment_tables['genres'][id_])
            director_full_list = self.get_dict_list_2col(augment_tables['directors'][id_])
            actors_full_list = self.get_dict_list_2col(augment_tables['actors'][id_])
            writers_full_list = self.get_dict_list_2col(augment_tables['writers'][id_])

            odd = {"id": id_,
                   "imdb_rating": rating,
                   #"genre": genres_list,
                   "title": title,
                   "description": description,
                   #"director": director_list,
                   "genres": genres_full_list,
                   #"actors_names": actors_names_list,
                   #"writers_names": writers_names_list,
                   "directors": director_full_list,
                   "actors": actors_full_list,
                   "writers": writers_full_list
                   }

            processed_data.append(odd)

        return processed_data
