#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Jorge Morgado <jorge (at) morgado (dot) ch>
#

"""
This module implements a generic MySQL database layer abstraction.

For the unit tests on this module to work, you need to setup a MySQL database
instance (and account) on the localhost as follows:

CREATE DATABASE test;
USE test;
CREATE TABLE test (
       id INTEGER NOT NULL AUTO_INCREMENT,
       col1 TEXT,
       col2 TEXT,
       PRIMARY KEY (id));
CREATE USER 'test'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES
      ON test.*
      TO 'test'@'localhost'
      WITH GRANT OPTION;
FLUSH PRIVILEGES;


To test the module use:
$ python db.py
"""

import mysql.connector

__author__ = "Jorge Morgado"
__copyright__ = "Copyright (c)2014, Jorge Morgado"
__credits__ = []
__license__ = "unknown"
__version__ = "1.0.0"
__maintainer__ = "Jorge Morgado"
__email__ = "jorge (at) morgado (dot) ch"
__status__ = "Production"

class Db():
    def __init__(self, dbuser, dbpass, dbname,
                 dbhost='127.0.0.1', dbport=3306, raise_on_warnings=True,
                 buffered_cursor=True):
        """ Connect to the `database`.

            Please note that the connection sets a buffered cursor by default.
            This is usually okay when fetching a small amount of data.
            Although, if you know the result has lots of data, it is generally
            safer to use non-buffering cursor. In this case, you will then
            have to consume *all* rows.

        >>> mydb = Db('test', 'password', 'test', '127.0.0.1')
        >>> mydb.close()

        >>> mydb = Db('baduser', 'password', 'test')
        Err 1045: Access denied for user 'baduser'@'localhost' (using password: YES)
        >>> mydb.close()

        >>> mydb = Db('test', 'badpass', 'test', '127.0.0.1')
        Err 1045: Access denied for user 'test'@'localhost' (using password: YES)
        >>> mydb.close()

        >>> mydb = Db('test', '', 'test')
        Err 1045: Access denied for user 'test'@'localhost' (using password: NO)
        >>> mydb.close()

        >>> mydb = Db('test', '', 'test', 'badhost')
        Err 2003: Can't connect to MySQL server on 'badhost:3306' (8)
        >>> mydb.close()

        >>> badport = 9999
        >>> mydb = Db('test', 'password', 'test', '127.0.0.1', badport)
        Err 2003: Can't connect to MySQL server on '127.0.0.1:9999' (61)
        >>> mydb.close()
        """

        dbconfig = {
            'user'              : dbuser,
            'password'          : dbpass,
            'database'          : dbname,
            'host'              : dbhost,
            'port'              : dbport,
            'raise_on_warnings' : raise_on_warnings,
            'autocommit'        : False,
        }

        try:
            self.conn = mysql.connector.connect(**dbconfig)

            # Create two cursors: one for RO and one for RW operartions
            self.cursor_ro = self.conn.cursor(buffered=buffered_cursor)
            self.cursor_rw = self.conn.cursor(buffered=buffered_cursor)
        except Exception as e:  # catch *all* exceptions
            print("Err %s" % e)


    def __del__(self):
        self.close()


    def close(self):
        """ Close the database connection.

        >>> mydb = Db('test', 'password', 'test', '127.0.0.1')
        >>> mydb.close()
        >>> mydb.close()
        """

        try:
            # Make sure data is commited to the database
            self.conn.commit()

            if self.cursor_ro is not None:
                self.cursor_ro.close()
            if self.cursor_rw is not None:
                self.cursor_rw.close()

            self.conn.close()
        except Exception:   # catch *all* exceptions
            pass            # but ignore them as we are closing


    def insert(self, table, record):
        """ Insert a new record into `table`. Returns the ID of the last
            inserted record.

        >>> mydb = Db('test', 'password', dbname='test', dbhost='127.0.0.1')
        >>> mydb.insert('test', { \
                    'col1': [ '%(col1)s', 'col1' ], \
                    'col2': [ '%(col2)s', 'col2' ], \
                }) > 0
        True
        >>> mydb.close()
        """

        columns_list = []
        values_list = []
        data_dict = {}
        query = 'INSERT INTO ' + table + ' ('

        for key, value in record.items():
            columns_list.append(key)
            values_list.append(value[0])
            data_dict[key] = value[1]

        query += ', '.join(columns_list) + ')'
        query += ' VALUES (' + ', '.join(values_list) + ')'

        self.cursor_rw.execute(query, data_dict)

        # Get the id of the last inserted recond and close the cursor
        return self.cursor_rw.lastrowid


    def update(self, table, record, where):
        """ Update the record with the given where clause.

        >>> mydb = Db('test', 'password', dbname='test', dbhost='127.0.0.1')
        >>> mydb.update('test', { \
                    'col1': '"newvalue1"', \
                    'col2': '"newvalue2"', \
                }, { \
                    'id': [ '%(id)s', 1 ], \
                })
        True
        >>> mydb.close()
        """

        set_list = []
        where_list = []
        data_dict = {}
        query = "UPDATE " + table + " SET "

        for key, value in record.items():
            set_list.append(key + ' = ' + value)

        for key, value in where.items():
            where_list.append(key + ' = ' + value[0])
            data_dict[key] = value[1]

        query += ', '.join(set_list)
        query += ' WHERE ' + ', '.join(where_list)

        self.cursor_rw.execute(query, data_dict)

        return True


    def select(self, table, cols='*', where=None, order=None, desc=False):
        """ Set the cursor from the search of all records that match the
            given `where` criteria.

        >>> mydb = Db('test', 'password', dbname='test', dbhost='127.0.0.1')
        >>> mydb.select('test')
        True
        >>> row = mydb.fetch_next()
        >>> row[0]
        1

        >>> mydb.select('test', \
                    [ 'id', 'col1' ], \
                    { 'id': [ ' = ', '%(id)s', '2' ] } \
                )
        True
        >>> row = mydb.fetch_next()
        >>> row[0]
        2
        >>> mydb.close()
        """

        query = "SELECT " + ', '.join(cols) + ' FROM ' + table

        if order is None:
            orderby = ''
        else:
            orderby = ' ORDER BY ' + ', '.join(order)

            if desc:
                orderby += " DESC"

        if where is None:
            self.cursor_ro.execute(query + ' ' + orderby)
        else:
            where_list = []
            data_dict = {}

            for key, value in where.items():
                where_list.append(key + value[0] + value[1])
                data_dict[key] = value[2]

            query += ' WHERE ' + ' and '.join(where_list) + orderby
            self.cursor_ro.execute(query, data_dict)

        return True


    def execute_sql(self, sql):
        """ Execute an SQL read query. """

        try:
            self.cursor_ro.execute(sql)
        except Exception as e:  # catch *all* exceptions
            print("Err %s" % e)
            raise e


    def fetch_next(self):
        """ Get the next row of a query result set, returning a single
            sequence, or None when no more rows are available. The returned
            tuple consists of data returned by the MySQL server converted to
            Python objects.
        """

        return self.cursor_ro.fetchone()


    def fetch_all(self):
        """ Get all rows of a query result set or None if no rows are
            available.
        """

        return self.cursor_ro.fetchall()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
