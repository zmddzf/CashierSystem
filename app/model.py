# -*- coding: utf-8 -*-
import pymysql
import datetime
class model:
    """
    Connect to the database and send sql command.
    
    Attributes:
        send_sql: to send sql command to the database.
        close: close the database connection.
    """
    def __init__(self, username, password, host):
        self.username = username
        self.password = password
        self.host = host
        self.db = pymysql.connect(self.host, self.username, self.password,charset = 'utf8')
        
    def send_sql(self, sql):
        cursor = self.db.cursor()
        print(sql)
        state = cursor.execute(sql)
        print(state)
        self.db.commit()
        
    def query(self, sql):
        cursor = self.db.cursor()
        cursor.execute(sql)
        info = cursor.fetchall()
        return info
        
    def close(self):
        self.db.close()
        print('The connection has been closed')
        
class user:
    
    def __init__(self, model):
        self.model = model
    
    def check_username(self, username):
        if self.model.query("SELECT USERNAME FROM SHANHUI.USERINFO WHERE USERNAME = '%s'"%username):
            return True
        else:
            return False
    
    def check_password(self, username, password):
        if password == self.model.query("SELECT PASSWORD FROM SHANHUI.USERINFO WHERE USERNAME = '%s'"%username)[0][0]:
            return True
        else:
            return False
    
    def register(self, username, password1, password2):
        if not self.model.query("SELECT USERNAME FROM SHANHUI.USERINFO WHERE USERNAME = '%s'"%username) and password1 == password2:
            self.model.send_sql("INSERT INTO SHANHUI.USERINFO VALUES ('"+username+"','"+password1+"')")
            return True
        else:
            return False

class order:
    
    def __init__(self, model):
        self.model = model
    
    def checkin_order(self, order_id, desk_id):
        try:
            self.model.send_sql("INSERT INTO SHANHUI.ORDER (ORDER_ID, CHECKIN_DATE, DESK_ID) VALUES('%s', '%s', '%s')"%(order_id, str(datetime.datetime.now()), desk_id))
            return True
        except:
            return False
    
    def checkout_order(self, order_id, discount, pay_mode):
        try:
            self.model.send_sql("UPDATE SHANHUI.ORDER SET DISCOUNT = '%s' WHERE ORDER_ID = '%s'"%(discount, order_id))
            self.model.send_sql("UPDATE SHANHUI.ORDER SET CHECKOUT_DATE = '%s' WHERE ORDER_ID = '%s'"%(str(datetime.datetime.now()), order_id))
            self.model.send_sql("UPDATE SHANHUI.ORDER SET PAY_MODE = '%s' WHERE ORDER_ID = '%s'"%(pay_mode, order_id))
            return True
        except:
            return False
        
    def total_info(self, desk_id):
        try:
            info = self.model.query("SELECT OI.`ORDER_ID`, D.`DISH_ID`, D.`DISH_NAME`, D.`DISH_PRICE`, OI.`ORDER_QUANTITY`, D.`DISH_PRICE` * OI.`ORDER_QUANTITY` AS TOTAL FROM `SHANHUI`.`DISH` D, `SHANHUI`.`ORDER_INFO` OI WHERE `SHANHUI`.OI.`ORDER_ID`=(SELECT `SHANHUI`.`ORDER`.`ORDER_ID` FROM `SHANHUI`.`ORDER` WHERE `SHANHUI`.`ORDER`.`CHECKOUT_DATE` IS NULL AND `SHANHUI`.`ORDER`.`DESK_ID`= '%s') AND D.`DISH_ID`= OI.`DISH_ID` GROUP BY OI.`ORDER_ID`, D.`DISH_ID`"%desk_id)
            return info
        except:
            return False
    
    def total_amount(self, desk_id):
        try:
            amount = self.model.query("SELECT SUM(TOTAL) FROM (SELECT D.`DISH_PRICE` * OI.`ORDER_QUANTITY` AS TOTAL FROM `SHANHUI`.`DISH` D, `SHANHUI`.`ORDER_INFO` OI WHERE `SHANHUI`.OI.`ORDER_ID`=(SELECT `SHANHUI`.`ORDER`.`ORDER_ID` FROM `SHANHUI`.`ORDER` WHERE `SHANHUI`.`ORDER`.`CHECKOUT_DATE` IS NULL AND `SHANHUI`.`ORDER`.`DESK_ID`= '%s') AND D.`DISH_ID`= OI.`DISH_ID` GROUP BY D.`DISH_ID`, OI.`ORDER_ID`) AS T1"%desk_id)
            return amount
        except:
            return False
        
    def showorder(self, order_id):
        try:
            order = self.model.query("SELECT `ORDER`.*, SUM(TOTAL) FROM(SELECT (D.`DISH_PRICE` * OI.`ORDER_QUANTITY` * O.`DISCOUNT` * 0.1)  AS TOTAL FROM `SHANHUI`.`DISH` D, `SHANHUI`.`ORDER_INFO` OI, `SHANHUI`.`ORDER` O WHERE `SHANHUI`.OI.`ORDER_ID` = '%s' AND D.`DISH_ID`= OI.`DISH_ID` AND O.`ORDER_ID` =OI.`ORDER_ID`  GROUP BY D.`DISH_ID`, OI.`ORDER_ID`, O.`ORDER_ID` ) AS T1, `SHANHUI`.`ORDER`WHERE `ORDER_ID` = '%s' GROUP BY `ORDER` .`ORDER_ID`"%(order_id, order_id))
            return order
        except:
            return False

    
    def show_all(self):
        try:
            all_order = self.model.query("SELECT O.*, SUM(T1.TOTAL)*O.DISCOUNT*0.1 FROM `SHANHUI`.`ORDER` O, (SELECT OI.`ORDER_ID`, (D.`DISH_PRICE` *OI.`ORDER_QUANTITY`) AS TOTAL FROM `SHANHUI`.`DISH` D, `SHANHUI`.`ORDER_INFO` OI WHERE OI.`DISH_ID` = D.`DISH_ID` GROUP BY OI.`ORDER_ID`, D.`DISH_ID`) T1 WHERE O.`ORDER_ID` = T1.`ORDER_ID` GROUP BY T1.`ORDER_ID`, O.`ORDER_ID`")
            return all_order
        except:
            return False

    
class orderinfo:
    
    def __init__(self, model):
        self.model = model
    
    def create_info(self, order_id, dish_id, quantity):
        self.model.send_sql("INSERT INTO SHANHUI.ORDER_INFO VALUES('%s', '%s', '%s')"%(order_id, dish_id, quantity))
        return True
    
    def get_info(self, order_id):
        try:
            info = self.model.query("SELECT * FROM SHANHUI.ORDER_INFO WHERE ORDER_ID = '%s'"%order_id)
            return info
        except:
            return False
    def get_desk_info(self, desk_id):
        try:
            info = self.model.query("SELECT `SHANHUI`.OI.`ORDER_ID`, `SHANHUI`.D.`DISH_ID`, `SHANHUI`.D.`DISH_NAME`, `SHANHUI`.OI.`ORDER_QUANTITY` FROM `SHANHUI`.`DISH` D, `SHANHUI`.`ORDER_INFO` OI WHERE `SHANHUI`.OI.`ORDER_ID`=(SELECT `SHANHUI`.`ORDER`.`ORDER_ID` FROM `SHANHUI`.`ORDER` WHERE `SHANHUI`.`ORDER`.`CHECKOUT_DATE` IS NULL AND `SHANHUI`.`ORDER`.`DESK_ID`= '%s') AND D.`DISH_ID`= OI.`DISH_ID` GROUP BY OI.`ORDER_ID`, D.`DISH_ID`, D.`DISH_NAME`, OI.`ORDER_QUANTITY`"%desk_id)
            return info
        except:
            return False
        
    def delete_info(self, order_id, dish_id):
        try:
            state = self.model.send_sql("DELETE FROM SHANHUI.ORDER_INFO WHERE ORDER_ID = '%s' AND DISH_ID = '%s'"%(order_id, dish_id))
            if state:
                return True
            else:
                return False
        except:
            return False
    
    def get_all(self):
        try:
            info = self.model.query('SELECT * FROM SHANHUI.ORDER_INFO')
            return info
        except:
            return False

class dish:
    
    def __init__(self, model):
        self.model = model
    
    def get_dishes(self):
        try:
            dishes = self.model.query('SELECT * FROM SHANHUI.DISH')
            return dishes
        except:
            return False
    
    def adddish(self, args):
        try:
            self.model.send_sql("INSERT INTO SHANHUI.DISH VALUES('%s', '%s', '%s', '%s')"%(args[0], args[1], args[2], args[3]))
            return True
        except:
            return False
    
    def updatedish(self, args):
        try:
            self.model.send_sql("UPDATE SHANHUI.DISH SET DISH_NAME = '%s' WHERE DISH_ID = '%s'"%(args[1], args[0]))
            self.model.send_sql("UPDATE SHANHUI.DISH SET DISH_PRICE = '%s' WHERE DISH_ID = '%s'"%(args[2], args[0]))
            self.model.send_sql("UPDATE SHANHUI.DISH SET DISH_DESCRIPTION = '%s' WHERE DISH_ID = '%s'"%(args[3], args[0]))
            return True
        except:
            return False

class desk:
    
    def __init__(self, model):
        self.model = model
    
    def get_desk(self):
        try:
            info = self.model.query("SELECT * FROM SHANHUI.DESK")
            return info
        except:
            return False
            
    def adddesk(self, args):
        try:
            self.model.send_sql("INSERT INTO SHANHUI.DESK VALUES('%s', '%s')"%(args[0], args[1]))
            return True
        except:
            return False
        
    def updatedesk(self, args):
        try:
            self.model.send_sql("UPDATE SHANHUI.DESK SET MAX_NUM = '%s' WHERE DESK_ID = '%s'"%(args[1], args[0]))
            return True
        except:
            return False
            
            
            
            
            
            