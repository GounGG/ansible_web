#!/usr/bin/python
# coding:utf-8

import pymysql
import ConfigParser

class Main():
    def __init__(self,sql):
        cf = ConfigParser.ConfigParser()
        cf.read("config/Config.ini")
        self.sql = sql
        self.host = cf.get('db', 'host')
        self.user = cf.get('db', 'user')
        self.passwd = cf.get('db', 'passwd')
        self.db = cf.get('db', 'db')

    def conn(self):
        conn = pymysql.connect(host=self.host,user=self.user, passwd=self.passwd, db=self.db, charset='utf8' )
        return conn

    def q_cursor(self):
         conn = self.conn()
         cur = conn.cursor()
         cur.execute(self.sql)
         return cur

    def u_cursor(self):
         conn = self.conn()
         cur = conn.cursor()
         cur.execute(self.sql)
         conn.commit()
         return cur

    def query(self):
        res = self.q_cursor()
        return res.fetchall()

    def insert(self):
        self.u_cursor()
