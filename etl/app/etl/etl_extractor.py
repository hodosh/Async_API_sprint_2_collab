import redis

from data_statemashine import JsonFileStorage, State
from etl_command import ETLCommand
from varparser import *
from setup_logging import *
from psycopg2 import OperationalError, errorcodes, errors

logger = get_logger()


class ETLExtractor(ETLCommand):
    def __init__(self, task, task_name, command_name, _redis: redis.Redis):
        super().__init__(task, task_name, command_name, _redis)
        self.log_signature('INIT')

        data_node_callable = self.task[command_name]['worker']
        self.data_node = data_node_callable()
        self.data_node.connect()

        self.modified_last_flag = False

    def run(self, data=None):
        self.log_signature('RUN')
        query = self.task[self.command_name]['sql_query']

        try:
            if self.data_node.connection == 0:
                self.data_node.connect()

            query = self.analyze_query(query, data)
            temp_data = self.data_node.pull(query)
            data[self.command_name] = temp_data
            return True

        except ValueError as err:
            logger.warning(f"DB Error: {err}")
            return False

    def commit(self, data=None):
        if self.modified_last_flag:
            if len(data[self.command_name]) > 0:
                modified_last = data[self.command_name][-1][1]
                modified_keystore = self.get_unique_key('modified_last')
                # logger.info(modified_last)
                self._redis.set(modified_keystore, str(modified_last))

        self.modified_last_flag = False

    def rollback(self, data=None):
        self.modified_last_flag = False

    def get_unique_key(self, suffix):
        return f"{self.task_name}__{self.command_name}__{suffix}"

    def analyze_query(self, query, data=None):
        if query.find('$batch_size') > -1:
            query = vars_parse_batch_size(query)

        if query.find('$modified_last') > -1:
            modified_default_value = datetime(1980, 1, 1, 1, 1, 1, 1)
            modified_keystore = self.get_unique_key('modified_last')
            modified_value = self._redis.get(modified_keystore)
            if not modified_value:
                modified_value = str(modified_default_value.strftime("%Y-%d-%m, %H:%M:%S"))

            self.modified_last_flag = True
            query = vars_parse_last_modified(query, last_modified=modified_value)

        if query.find('$list_id') > -1:
            depends_on_command = self.task[self.command_name]['depends_on']
            depends_on_set = data[depends_on_command]

            list_id = []
            for row in depends_on_set:
                list_id.append(row[0])

            # logger.info(list_id)

            query = vers_parse_list_id(query, list_id=list_id)

        # logger.info(query)
        return query
