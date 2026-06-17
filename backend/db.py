import pymysql
from config import Config

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = None
        return cls._instance

    def connect(self):
        try:
            self.connection = pymysql.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False
            )
        except Exception as e:
            print(f"数据库连接失败: {e}")
            raise

    def get_cursor(self):
        if not self.connection or not self.connection.open:
            self.connect()
        return self.connection.cursor()

    def execute_query(self, sql, params=None):
        cursor = self.get_cursor()
        cursor.execute(sql, params)
        result = cursor.fetchall()
        cursor.close()
        return result

    def execute_one(self, sql, params=None):
        cursor = self.get_cursor()
        cursor.execute(sql, params)
        result = cursor.fetchone()
        cursor.close()
        return result

    def execute_update(self, sql, params=None):
        cursor = self.get_cursor()
        affected = cursor.execute(sql, params)
        self.connection.commit()
        cursor.close()
        return affected

    def execute_insert(self, sql, params=None):
        cursor = self.get_cursor()
        cursor.execute(sql, params)
        self.connection.commit()
        new_id = cursor.lastrowid
        cursor.close()
        return new_id

    def call_procedure(self, proc_name, args=None):
        cursor = self.get_cursor()
        cursor.callproc(proc_name, args)
        result = cursor.fetchall()
        self.connection.commit()
        cursor.close()
        return result

    def close(self):
        if self.connection and self.connection.open:
            self.connection.close()

db = Database()