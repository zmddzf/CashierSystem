# -*- coding: utf-8 -*-
from flask import Flask
app = Flask(__name__)
from app import views
from app import model
 
if __name__ == "__main__":
     app.run()