# -*- coding: utf-8 -*-
from flask import Flask
app = Flask(__name__)
from app import views
from app import model
from flask_session import Session
import os

app.config['SESSION_PERMANENT'] = True
app.config['SECRET_KEY'] = '1w1e1r2t3y4u5i6ioh2nkl35'
app.config['SESSION_TYPE'] = 'memcached'



if __name__ == "__main__":
    app.run()
