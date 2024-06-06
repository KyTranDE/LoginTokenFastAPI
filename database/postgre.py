import psycopg2
from tabulate import tabulate
import pandas as pd
import emoji
import os
from os.path import join
import datetime
from dotenv import load_dotenv

dotenv_path = '.env'
load_dotenv(dotenv_path)

HOST = os.getenv('DB_HOST')
USER = os.getenv('DB_USER')
PORT = os.getenv('DB_PORT')
PASSWORD = os.getenv('DB_PASSWORD')
DATABASE = os.getenv('DB_DATABASE')
 
class PostgresTool():
    def __init__(self, host, user, port, password, database):
        self.host = host
        self.user = user
        self.port = port
        self.password = password
        self.database = database

        self.conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            port=port,
            password=password
        )
        self.cur = self.conn.cursor()
    
    def close(self):
        self.cur.close()
        self.conn.close()

    def query(self, sql_query, show=True):
        self.cur.execute("ROLLBACK")
        self.cur.execute(sql_query)
        if show:
            rows = self.cur.fetchall()
            print(tabulate(rows, headers=[desc[0] for desc in self.cur.description], tablefmt='psql'))
        else:
            return self.cur.fetchall()
        
    def get_columns(self, table_name):
        self.cur.execute("ROLLBACK")
        self.cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name = '{table_name}'".format(table_name=table_name))
        cols = [i[0] for i in self.cur.fetchall()]
        return cols

    def get_all_table(self,):
        self.cur.execute("ROLLBACK")
        self.cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE'")
        tables = [i[0] for i in self.cur.fetchall()]
        return tables
    
    def insert_data(self, path_csv):
        df = pd.read_csv(path_csv)
        table_name = path_csv.split('/')[-1].split('\\')[-1].split('//')[-1].split('.')[0]
        list_columns = list(df.columns)
        try:
            for index, row in df.iterrows():
                columns = ', '.join([f'"{col}"' for col in list_columns])
                values = ', '.join(['%s' for _ in range(len(list_columns))])
                insert_stmt = f'INSERT INTO "{table_name}" ({columns}) VALUES ({values})'
                self.cur.execute(insert_stmt, tuple(row))
                print(emoji.emojize(":check_mark_button: Data inserted successfully! :check_mark_button:"))
            self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            error_message = f":cross_mark: {str(e)}"
            print(emoji.emojize(error_message))

    def push_data(self, table_name: str = None, df: pd.DataFrame = None, skip_cols=[]):
        if df is None:
            print(emoji.emojize(":cross_mark: DataFrame is None!"))
            return {"status": "error", "message": "DataFrame is None"}
        
        # Remove the columns to be skipped
        df = df.drop(columns=skip_cols, errors='ignore')
        list_columns = list(df.columns)

        try:
            for index, row in df.iterrows():
                columns = ', '.join([f'"{col}"' for col in list_columns])
                values = ', '.join(['%s' for _ in range(len(list_columns))])
                insert_stmt = f'INSERT INTO "{table_name}" ({columns}) VALUES ({values})'
                self.cur.execute(insert_stmt, tuple(row))
            self.conn.commit()
            success_message = ":check_mark_button: Data pushed successfully! :check_mark_button:"
            print(emoji.emojize(success_message))
            return {"status": "success", "message": success_message}
        except psycopg2.Error as e:
            self.conn.rollback()
            error_message = f":cross_mark: {str(e)}"
            print(emoji.emojize(error_message))
            return {"status": "error", "message": str(e)}