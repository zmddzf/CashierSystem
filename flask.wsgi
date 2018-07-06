import sys
sys.path.insert(0, "/var/www/web") #工程根目录，即wsgi文件的路径
from app import app as application