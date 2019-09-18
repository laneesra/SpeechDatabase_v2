import psycopg2 as pg
import os

class speech_db:
    def open_conn(self):
        conn = pg.connect(dbname='speech', user='postgres', password='123456', host='localhost')
        cursor = conn.cursor()
        return conn, cursor

    def close_conn(self, conn, cursor):
        cursor.close()
        conn.close()

    def get_field_names(self, table):
        conn, cursor = self.open_conn()
        cursor.execute("SELECT column_name, data_type from information_schema.columns where table_name = '{}';".format(table))
        res = [c for c in cursor]
        print(res)
        self.close_conn(conn, cursor)

    def get_filename(self, base_filename, source_subdir, source_name):
        conn, cursor = self.open_conn()
        cursor.execute("SELECT file_extension, source_dir FROM voice_and_source WHERE base_filename = '{}' AND "
                       "source_name = '{}'".format(base_filename, source_name))
        file = cursor.fetchone()
        filename = os.path.join(file[1], source_subdir, base_filename + '.' + file[0])
        self.close_conn(conn, cursor)
        return filename

    def split_full_path_to_fields(self, source_dir, full_path):
        dict = {}
        dict['source_dir'] = source_dir
        dict['source_subdir'] = full_path[len(source_dir):]
        base_filename = os.path.split(full_path)[-1].split('.')
        dict['base_filename'] = base_filename[0]
        dict['file_extension'] = base_filename[1]
        return dict

    def insert_to_table_one(self, table: str, fields: list, values: list):
        """
        inserting one item to table
        input:
            table: str // table name
            fields: list[str] // field names (e. g. ['file_extension', 'frame_rate'])
            values: list[Any] // field values (e. g. ['wav', 16000])
        output: None
        """
        conn, cursor = self.open_conn()
        fields_str = ''
        values_str = ''
        for f in fields:
            fields_str += f + ', '
            values_str += '%s, '
        fields_str = fields_str[:-2]
        values_str = values_str[:-2]

        sql = 'INSERT INTO {}({}) VALUES({});'.format(table, fields_str, values_str)
        cursor.execute(sql, values)
        print(cursor.statusmessage)
        conn.commit()
        self.close_conn(conn, cursor)


    def insert_to_table_many(self, table: str, fields: list, values: list):
        """
        inserting many items to table
        input:
            table: str // table name
            fields: list[str] // field names (e. g. ['file_extension', 'frame_rate'])
            values: list[dict] // list of dicts (e. g. [{'file_extension': 'wav', 'frame_rate': 16000}, {'file_extension': 'mp3', 'frame_rate': 16000}])
        output: None
        """
        conn, cursor = self.open_conn()
        fields_str = ''
        values_str = ''
        for f in fields:
            fields_str += f + ', '
            values_str += '%({})s, '.format(f)
        fields_str = fields_str[:-2]
        values_str = values_str[:-2]
        sql = 'INSERT INTO {}({}) VALUES({});'.format(table, fields_str, values_str)
        cursor.executemany(sql, values)
        print(cursor.statusmessage)
        conn.commit()
        self.close_conn(conn, cursor)

    def update_one(self, table: str, filter: str, fields: list, values: list):
        """
        updating item by filter
        input:
            table: str // table name
            filter: str or nothing // filter (e. g. "snr > 50", "source = 'common_voice'")
            fields: list[str] // field names (e. g. ['file_extension', 'frame_rate'])
            values: list[Any] // field values (e. g. ['wav', 16000])
        output: None
        """
        conn, cursor = self.open_conn()
        set_str = ''
        for i in range(len(fields)):
            if isinstance(values[i], str):
                set_str += "{} = '{}', ".format(fields[i], values[i])
            else:
                set_str += "{} = {}, ".format(fields[i], values[i])
        set_str = set_str[:-2]
        sql = "UPDATE {} SET {} WHERE {}".format(table, set_str, filter)
        cursor.executemany(sql, values)
        print(cursor.statusmessage)
        conn.commit()
        self.close_conn(conn, cursor)

    def select_from_table(self, table: str, filter: str = '', return_fields: list = [], optional: str  = '') -> list:
        """
        selecting all/exact fields from table with/without filter
        input:
            table: str // table name
            filter: str or nothing // filter (e. g. "snr > 50", "source = 'common_voice'")
            return_fields: list[str] or nothing // field names to return (nothing = all fields)
            optional: str // additional sql commands (e. g. "ORDER BY snr")
        output: list
        """
        conn, cursor = self.open_conn()
        if len(return_fields):
            return_str = ''
            for f in return_fields:
                return_str += f + ', '
            return_str = return_str[:-2]
        else:
            return_str = '*'
        sql = 'SELECT {} FROM {}'.format(return_str, table)
        if filter != '':
            sql += ' WHERE {}'.format(filter)
        if optional != '':
            sql += ' ' + optional

        cursor.execute(sql)
        print(cursor.statusmessage)
        res = [c for c in cursor]
        conn.commit()
        self.close_conn(conn, cursor)
        return res

if __name__ == '__main__':
    db = speech_db()

    '''res = db.select_from_table('voice', "source_name = 'common_voice' AND file_extension = 'mp3'", [], 'ORDER BY base_filename LIMIT 10')
    for r in res:
        filename = db.get_filename(r[4], r[5], r[6])
        print(filename)
    db.get_field_names('voice')
    db.get_field_names('source')'''
