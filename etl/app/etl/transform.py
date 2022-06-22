import abc

from setup_logging import *

logger = get_logger()


class Transform:
    """
    Абстрактный класс Трансформер.

    """

    def __init__(self, task):
        self.task = task

    def get_plain_list(self, data):
        return ",".join(f"{str(x[1])}" for x in data)

    def get_dict_list_2col(self, data):
        temp_list = []
        for row in data:
            temp_dict = {
                'id': row[0],
                'name': row[1]
            }
            temp_list.append(temp_dict)

        return temp_list

    def get_dict_labeled_list(self, labels, data):
        temp_list = []
        for row in data:
            temp_dict = dict(zip(labels, row[0:1]))
            temp_list.append(temp_dict)
        return temp_list


    def get_dict_list_2col(self, data):

        temp_list = []
        for row in data:
            temp_dict = {
                'id': row[0],
                'name': row[1]
            }
            temp_list.append(temp_dict)

        return temp_list

    def get_dict_list_1col(self, data):
        temp_list = []
        for row in data:
            temp_dict = {
                'id': row[0],
            }
            temp_list.append(temp_dict)

        return temp_list

    @abc.abstractmethod
    def transform(self, data_table, augment_tables):
        pass
