import backoff
from psycopg2 import InterfaceError

from datanode import DataNode
from pg_adapter import *
from setup_logging import *

logger = get_logger()
load_dotenv()


def backoff_handler(details):
    logger.warning("PG Connect  - Backing off {wait:0.1f} seconds after {tries} tries ".format(**details))


class DataNodePostgres(DataNode):
    def __init__(self):
        self.connection = None
        self.connect()

    @backoff.on_exception(backoff.expo,
                          (OperationalError, InterfaceError),
                          max_time=60,
                          on_backoff=backoff_handler)
    def connect(self):
        conn = PGAdapter.get_instance()
        self.connection = conn.get_connection()

    def pull(self, sql_query):
        try:
            # if self.connection is None:
            #     self.connect()

            cur = self.connection.cursor()
            cur.execute(sql_query)
            batch_size = int(os.environ.get('BATCH_SIZE'))
            results = cur.fetchmany(batch_size)
            return results

        except (OperationalError, InterfaceError, Exception) as err:
            self.connect()
            raise ValueError(err.args)

    def push(self, data):
        pass
