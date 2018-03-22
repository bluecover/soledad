#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import glob
import os
import re
import sys
import traceback
import warnings
import optparse

from MySQLdb import ProgrammingError


class NotTestingDatabaseException(Exception):
    def __str__(self):
        return ('The database name must starts with "test_", '
                'else real database may be destoried!')


def init_db(store, tables, init_data=None):
    # 机器重启后，内存表中数据会全丢，必须重新建表、初始化数据。
    # 通过global_ids表中记录数可以判断机器是否重启过
    force = True
    init_db_tables(store, tables, force=force)

RE_ENGINE = re.compile(r'(?i)(?<= ENGINE=)(\w+)(?=\s|$)')
RE_BLOB = re.compile(r'(?i)(?<=` )(\w*text|blob)(?=\s|,)')
RE_FULLTEXT = re.compile(r'(?im)(,\n\s*FULLTEXT KEY[^,\n]*)(?=,|\n)')
RE_TABLE_OPTIONS = re.compile('(ROW_FORMAT|KEY_BLOCK_SIZE)=\S+')


def change_memory_engine(sql_create, blob_length=3000):
    if os.environ.get('NOT_MEMORY_ENGINE_DB'):
        return sql_create
    # change engine to MEMORY
    sql = RE_ENGINE.sub('MEMORY', sql_create)
    # remove incompatible table options
    sql = RE_TABLE_OPTIONS.sub('', sql)
    # `MEMORY tables cannot contain BLOB or TEXT columns.'
    #  -- http://dev.mysql.com/doc/refman/5.0/en/memory-storage-engine.html
    # so change TEXT or BLOB to varchar
    sql = RE_BLOB.sub('varchar(%s)' % blob_length, sql)
    # `FULLTEXT indexes are supported only for MyISAM tables ...'
    #  -- http://dev.mysql.com/doc/refman/5.0/en/create-index.html
    # so remove fulltext key
    sql = RE_FULLTEXT.sub('', sql)
    return sql


def run_sql(cursor, sql, *params):
    return cursor.execute(sql, params)


def run_sql2(cursor, sql, *params):
    '''print sql execute time'''
    s = datetime.datetime.now()
    ret = cursor.execute(sql, params)
    e = datetime.datetime.now()
    print e - s, sql[:60].replace('\n', r'\n')
    return ret


def table_schema_changed(cursor, table_name, new_schema):
    if table_name in ['artist', 'minisite']:
        return 'renew'

    try:
        run_sql(cursor, 'show create table `%s`' % table_name)
    except ProgrammingError, e:
        if "doesn't exist" in str(e):
            return 'not exists'
        raise e
    row = cursor.fetchone()
    name, schema = row

    def normal(line):
        norm = line.upper().replace('  ', ' ')
        if 'VARCHAR(3000)' in norm:
            norm = norm.replace(' DEFAULT NULL', '')
        if ' USING BTREE' in norm:
            norm = norm.replace(' USING BTREE', '')
        return norm

    orig = [normal(s) for s in schema.split('\n') if s.startswith('  ')]
    new = [normal(s) for s in new_schema.split('\n') if s.startswith('  ')]
    if orig != new:
        return 'changed'
    if run_sql(cursor, 'select * from `%s` limit 1' % table_name):
        return 'has data'
    return False


def init_db_tables(store, tables, force=False):
    if not store.is_testing():
        raise NotTestingDatabaseException()
    cursor = store.get_cursor()
    for name in sorted(tables):
        sql = tables[name]
        sql = change_memory_engine(sql)
        try:
            if force:
                changed = True
            else:
                changed = table_schema_changed(cursor, name, sql)
        except Exception, e:
            traceback.print_exc(e)
            raise e
        if not changed:
            continue
        if changed != 'not exists':
            run_sql(cursor, 'DROP TABLE IF EXISTS `%s`' % name)
            # print 'table', name, 'schema changed'
        try:
            sql = sql.replace('%', '%%')
            run_sql(cursor, sql)
        except Exception, e:
            print sql
            traceback.print_exc(e)
            raise e


def load_db_data(store, data):
    if not store.is_testing():
        raise NotTestingDatabaseException()
    cursor = store.get_cursor()
    convert = False
    for sql in data:
        sql = sql.replace('%', '%%')
        if convert:
            sql = sql.decode('utf8')
        try:
            try:
                run_sql(cursor, sql)
            except UnicodeDecodeError:
                convert = True
                run_sql(cursor, sql.decode('utf8'))
        except Exception, e:
            print sql
            traceback.print_exc(e)
            raise e
    cursor.connection.commit()


def read_tables(sql_dump_file):
    """read tables create sql from mysql dump file

    input: sql_dump_file, <file> object
    output: dict of {table_name: create_sql}
    """

    tables = {}
    in_create = False
    table_name = ''
    create = []
    for line in sql_dump_file:
        if line.startswith('CREATE TABLE `'):
            in_create = True
            table_name = line[len('CREATE TABLE `'):-len("' (\n")]
            create = [line]
        elif in_create:
            if line.startswith(')'):
                create.append(line)
                in_create = False
                tables[table_name] = ''.join(create)
                create = []
            elif not (line.startswith('--') or line.startswith('/*')):
                create.append(line)
    return tables


def read_data(table_data):
    for line in table_data:
        if line.startswith('INSERT INTO '):
            yield line
        elif line.startswith('ALTER TABLE '):
            yield line


def read_sql_dir(dir, prefix):
    for path in glob.glob(dir + '/' + prefix + '*.sql'):
        f = file(path)
        for line in f:
            yield line


def init_db_from_dir(store, dir):
    tables = read_sql_dir(dir, 'schema')
    init_db(store, read_tables(tables))
    tables = read_sql_dir(dir, 'dev')
    init_db(store, read_tables(tables))

if __name__ == '__main__':
    from libs.utils.log import bcolors

    warnings.filterwarnings('ignore', 'Unknown table.*')

    parser = optparse.OptionParser()
    # parser.add_option('-v', '--verbose', action='store_true')
    # parser.add_option('-q', '--quiet', action='store_true')
    # parser.add_option('-m', '--use-memory', action='store_true',
    #         help='use mysql memory engine for testing')
    parser.add_option(
        '-n', '--not-testing-database', action='store_true',
        help='use database in config. but the database name must starts '
        'with "test" or "sandbox")')
    parser.add_option(
        '-d', '--sql-schema-dir', type='string',
        help='load sql schema files from SQL_SCHEMA_DIR',
        default='database')
    global options
    options, args = parser.parse_args()

    test_dir = os.path.dirname(os.path.realpath(__file__))
    shire_dir = os.path.dirname(test_dir)
    sys.path.append(shire_dir)

    store = None
    if options.not_testing_database:
        pass
    else:
        from tests.framework import init
        store = init()
    init_db_from_dir(store, options.sql_schema_dir)
    bcolors.success('Init db done.')
