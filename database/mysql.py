import mysql.connector
from tabulate import tabulate
import pandas as pd
import numpy as np
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

class MySql():
    def __init__(self, host=HOST, user=USER, port=PORT, password=PASSWORD):
        self.db = None
        self.cursor = None
        try:
            self.db = mysql.connector.connect(
                host=host,
                user=user,
                port=port,
                password=password,
                # database=database,
                auth_plugin='mysql_native_password'
            )
            self.cursor = self.db.cursor()
            print("connect to")
        except Exception as e:
            # self.db.close()
            print(f'Fail to connect to MySQL: {e}')
            
    def use_db(self, database):
        self.cursor.execute(f'USE {database};')
        self.db.commit()
        print(f'🔌 Use database {database}')
    def close(self):
        '''
        use to close to MySQL
        '''
        self.cursor.close()
        self.db.close()

    def query(self, text, show=True, fmt = 'psql',  df=False):
        '''
        use to query to MySQL
        '''
        self.cursor.execute(text)
        if show:
            print(tabulate(self.cursor.fetchall(), headers=self.cursor.column_names, tablefmt=fmt))
        else:
            if df:
                return pd.DataFrame(self.cursor.fetchall(), columns=self.cursor.column_names)
            return self.cursor.fetchall()
    
    def create_schema(self, sql_path):
        '''
        use to create tables on the database and link them together
        '''
        with open(sql_path, 'r') as f:
            schema = f.read().split('\n\n')
        try:
            for statement in schema:
                self.cursor.execute(statement)
                if statement.find('CREATE TABLE') != -1:
                    print(f'📢 Created table {statement.split("`")[1]}')
                if statement.find('ALTER TABLE') != -1:
                    alter = statement.split("`")
                    print(f'🔌 Linked table {alter[1]} -> {alter[5]}')
            self.db.commit()
        except Exception as e:
            print(f'❌ {e}')
    
    def get_data(self, df):
        '''
        use to get data from csv file
        '''
        df = df[self.columns]
        data = np.where(pd.isna(df), None, df).tolist()
        data = [tuple(i) for i in data]
        return data
        
    def push_data(self, table_name: str = None, df: list = None, skip_cols=[]):
        '''
        use to push data to database
        '''
        cols = self.query(f'SHOW COLUMNS FROM {table_name};', show=False)
        cols = [i[0] for i in cols]
        if skip_cols:
            for col in skip_cols:
                cols.remove(col)
        df = df[cols]
        datas = [tuple(i) for i in np.where(pd.isna(df), None, df).tolist()]
        
        sql_insert = f"insert into {table_name} ({','.join(cols)}) values ({','.join(['%s']*len(cols))})"
        self.cursor.executemany(sql_insert, datas)
        self.db.commit()
        
        return True
        # anno = f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] '
        # # anno +=sql_insert
        # try:
        #     self.cursor.executemany(sql_insert, datas)
        #     self.db.commit()
        # #     anno += 'success'
        # # for data in datas:
        # #     anno = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")},{",".join(map(str, data))},'
        # #     try:
        # #         self.cursor.execute(sql_insert, data)
        # #         anno += 'success'
        # #     except Exception as e:
        # #         anno += str(e)
        # #         continue
        # except Exception as e:
        
        #     pass
        #     anno += str(e)
        # # logger
        # path_log = f'logs/insert_db.log'
        # # os.makedirs(f'{"/".join(path_log.split("/")[:-1])}', exist_ok=True)
        # with open(f'{path_log}', 'a+', encoding='utf-8') as f:
        #     f.write(str(anno) + '\n')
    def update(self, table_name:str=None, df=None, cols_update:list=['sp_rl', 'total', 'ml'], condition:str='id'):
        for i in range(len(df)):
            sql_update = f"update {table_name} set {', '.join([f'{col}=%s' for col in cols_update])} where {condition}='{df.iloc[i][condition]}'"
            update_items = []
            for col in cols_update:
                if type(df.iloc[i][col]) == np.int64:
                    update_items.append(int(df.iloc[i][col]))
                else:
                    update_items.append(df.iloc[i][col])
            self.cursor.execute(sql_update, tuple(update_items))
            # self.cursor.execute(sql_update, tuple(df.iloc[i][col] for col in cols_update))
        self.db.commit()
    
    def check_dupli_user_or_email(self, email):
        '''
        use to check duplicate user or email
        '''
        self.cursor.execute(f"SELECT * FROM users WHERE email = '{email}';")
        result = self.cursor.fetchall()
        if result:
            return True
        return False

    def update_user(self, user: dict):
        '''
        use to update user
        '''
        sql_update = f"update users set password='{user['password']}', phone_number='{user['phone_number']}', full_name='{user['full_name']}' where email='{user['email']}'"
        self.cursor.execute(sql_update)
        self.db.commit()
        return True
    def delete(self, table_name:str=None, email:str=None):
        '''
        use to delete user
        '''
        self.cursor.execute(f"delete from {table_name} where email='{email}'")
        self.db.commit()
        return True