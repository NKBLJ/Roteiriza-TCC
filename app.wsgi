#!/usr/bin/python3
from wsgiref.handlers import CGIHandler

import os
from sys import path
path.insert(0, '/home1/emp23242/roteiriza.com.br/cgi-bin/venv/lib/python3.6/site-packages')
path.insert(0, '/home1/emp23242/roteiriza.com.br/cgi-bin/')
from app import app as application

os.environ['SCRIPT_NAME'] = ''
os.environ['REQUEST_METHOD'] = 'GET'
os.environ['FOLIUM_NO_MAP_INTERNALS'] = '1'

CGIHandler().run(application)
