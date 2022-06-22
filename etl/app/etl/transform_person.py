from setup_logging import *
from transform import Transform

logger = get_logger()


class TransformPerson(Transform):
    def transform(self, data_table, augment_tables):
        processed_data = []
        for item in data_table:
            (id_, modified, name_) = item

            roles_plain_list = self.get_plain_list(augment_tables['movies'][id_])
            # movies_full_list = self.get_dict_list_1col(augment_tables['movies'][id_])
            # movies_full_list = self.get_dict_labeled_list(['id', 'role'], augment_tables['movies'][id_])
            movies_full_list = self.get_dict_list_2col(augment_tables['movies'][id_])

            odd = {"id": id_,
                   "full_name": name_,
                   #"role": roles_plain_list,
                   "film_roles": movies_full_list
                   }

            processed_data.append(odd)

        return processed_data
