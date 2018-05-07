#!/usr/bin/env python
# coding=utf-8

import pymssql
import logging
from xutils import encode_utf8

LOGIN_TIMEOUT = 12
      
class MssqlAuth:
    def __init__(self, (host,port)):
        self.addr = (host, port)

    def login(self, username, password, timeout=LOGIN_TIMEOUT):
        conn_ok, auth_ok, banner = False, False, ''
        connection = None
        try:
            connection = pymssql.connect(server=self.addr[0],port=self.addr[1],
                                         user=username,password=password,
                                         database='master',login_timeout=LOGIN_TIMEOUT)
            conn_ok = True
            auth_ok = True
            cursor = connection.cursor()
            cursor.execute('SELECT @@VERSION')
            row = cursor.fetchone()
            banner = str(row[0])
            cursor.close()
            logging.getLogger().warn('FOUND %s:%s@%s:%d<OK>'%(username, password, self.addr[0], self.addr[1]))
        except Exception as e:
            es = str(e)
            #message 20002 -> auth failed
            #message 20009 -> connection refused
            #message 18456 -> auth failed
            if es.find('message 20009')>=0:
                logging.getLogger().info('ECON:1 %s:%d X' % (self.addr[0], self.addr[1]))
            elif es.find('message 20002')>=0 or es.find('message 18456')>=0:
                conn_ok = True
            else:
                conn_ok = True
                logging.getLogger().info('ERR:1 %s:%d %s' % (self.addr[0], self.addr[1], es))
        if connection:
            connection.close()
        del connection
        return conn_ok, auth_ok, banner


class MssqlBruteTester:
    def __init__(self, passlist, username='sa'):
        self.passlist = passlist
        pass
    
    def test(self, task):
        (host,port) = (task[0],task[1])
        rs = []
        auth = MssqlAuth( (host, port) )
        #for username in self.userdict:
        for password in self.passlist:
            conn_ok, auth_ok, banner = auth.login(username, password)
            if not conn_ok:
		print("conn failed!")
                return rs
            if not auth_ok:
		print("user:%s ,pass:%s login failed!"% (username, password))
                continue
            rs.append([host, port, 'MSSQL', username, password, encode_utf8(banner)])
	    print("user:%s ,pass:%s login ok!"% (username,password))
            break
        if not rs:
           logging.getLogger().info('SAFE %s:%d'%(host, port)) 
        return rs


if __name__=='__main__':
    import sys
    import xutils
    if len(sys.argv)!=5:
	print("usage:x.py host port passdictPath pathoflogfile")
	exit(0)
    host,port = sys.argv[1],int(sys.argv[2])
    
    passdict = []
    for ln in open(sys.argv[3]):
        #fs = ln.strip().split(':',1)
        #if len(fs)!=2:
        #    continue
        username = "sa"
        password = ln.strip()
        #if username not in userdict:
        #    userdict[username] = set()
        #userdict[username].add(password)
	#print(password)
	passdict.append(password)
    logger = xutils.initLogger(sys.argv[4])
    tester = MssqlBruteTester(passdict)
    rs = tester.test( (host,port) )
    print rs
    
