# -*- coding: utf-8 -*-

from app import app
import os
from datetime import timedelta


app.config['PERMANENT_SESSION_LIFETIME']=timedelta(days=7)
app.secret_key = os.urandom(24)
app.debug = True
app.run()