class MysqlConnPool(object):
    def __init__(self, master, slave, max_conn = 30):
        self.max_conn = max_conn
        self.lock = threading._allocate_lock()
        self.curr = 0
        self.conn_list = []

        i = 0
        while i < self.max_conn:
            self.conn_list.append(MysqlClient(master, slave))
            i += 1

    def _getConns(self):
        self.lock.acquire()
        conn = self.conn_list[self.curr]
        self.curr = (self.curr + 1) % self.max_conn
        self.lock.release()

        return conn

    def execute_query(self, db_name, sql, params=None):
        conn = self._getConns()
        rows = conn.execute_query(db_name, sql, params)

        return rows

    def execute_update(self, db_name, sql, params=None):
        conn = self._getConns()
        rows = conn.execute_update(db_name, sql, params)

        return rows

