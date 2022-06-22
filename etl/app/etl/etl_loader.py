from etl_command import ETLCommand
from setup_logging import *

logger = get_logger()


class ETLLoader(ETLCommand):
    def __init__(self, task, task_name, command_name):
        super().__init__(task, task_name, command_name)
        self.log_signature('INIT')

        data_node_callable = self.task[command_name]['worker']

        self.depends_on = self.task[command_name]['depends_on']
        self.es_index = self.task[command_name]['es_index']

        self.data_node = data_node_callable()
        self.data_node.connect(self.es_index)

    def run(self, data=None):
        self.log_signature('RUN')

        data[self.command_name] = self.data_node.push(data[self.depends_on])
        return True
