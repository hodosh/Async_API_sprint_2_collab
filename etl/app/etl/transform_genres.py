from setup_logging import *
from transform import Transform

logger = get_logger()


class TransformGenres(Transform):
    def transform(self, data_table, augment_tables):
        processed_data = []
        for item in data_table:
            (id_, modified, name_, description) = item

            movies_full_list = self.get_dict_list_1col(augment_tables['movies'][id_])

            odd = {"id": id_,
                   "name": name_,
                   "description": description,
                   "film_ids": movies_full_list
                   }

            processed_data.append(odd)

        return processed_data
