# -*- coding:utf-8 -*-
# Python3
# File    : run.py
# Time    : 2018/7/22 23:55
# Author  : Shaweb

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from new_app import app

http_server = HTTPServer(WSGIContainer(app))
http_server.listen(3001)  #flask默认的端口
IOLoop.instance().start()