# -*- coding: utf-8 -*-
"""
Created on Sun Jul  1 16:00:38 2018

@author: zmddzf
"""


from app import app
from app.model import model, user, order, orderinfo, dish, desk
from flask import render_template, redirect,url_for
from flask import request, session, g
import re


@app.route('/login', methods = ['GET', 'POST']) 
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = model('dzf', '123456', '39.108.102.21')
        usr = user(db)
        if usr.check_username(username):
            if usr.check_password(username, password):
                session['username'] = username
                db.close()
                return redirect('/workshop')
            else:
                db.close()
                return render_template('login.html', error = '请输入正确的密码！')
        else:
            db.close()
            return render_template('login.html', error = '账号错误！')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'GET':
        if 'username' in session:
            return render_template('register.html', back = '返回')
        else:
            return "PLEASE LOGIN!"
    if request.method == 'POST' and 'username' in session:
        username = request.form['username']
        password1 = request.form['password1']
        password2 = request.form['password2']
        db = model('dzf', '123456', '39.108.102.21')
        usr = user(db)
        if usr.register(username, password1, password2):
            db.close()
            return render_template('login.html')
        else:
            error = '用户名重复或两次密码不一致！'
            db.close()
            return render_template('register.html', error = error, back = '返回')
        
        
@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username', None)
        return render_template('login.html')
    else:
        return render_template('login.html')

@app.route('/workshop')
def workshope():
    if 'username' in session:
        return render_template('base2.html')
    else:
        return 'PLEASE LOGIN!'

@app.route('/orderdish', methods = ['GET', 'POST'])
def orderdish():
    if request.method == 'GET':
        if 'username' in session:
            db = model('dzf', '123456', '39.108.102.21')
            dish_t = dish(db)
            dishes = dish_t.get_dishes()
            return render_template('orderdish.html', dishes = dishes)
        else:
            return 'PLEASE LOGIN!'
    if request.method == 'POST':
        db = model('dzf', '123456', '39.108.102.21')
        order_t = order(db)
        orderinfo_t = orderinfo(db)
        dish_t = dish(db)
        global order_id
        global desk_id
        if 'username' in session:
            print(('desk_id' in request.form) and ('order_id' in request.form))
            if ('desk_id' in request.form) and ('order_id' in request.form):
                desk_id = request.form['desk_id']
                order_id = request.form['order_id']
                order_t.checkin_order(order_id, desk_id)
                dishes = dish_t.get_dishes()
                success = '创建成功！'
                return render_template('orderdish.html',success = success, dishes = dishes, desk_id = desk_id, order_id = order_id)
            else:
                dish_id = request.form['dish_id']
                quantity = request.form['quantity']
                dishes = dish_t.get_dishes()
                if orderinfo_t.create_info(order_id, dish_id, quantity):
                    print('problem\n\n\n\n')
                order_info = orderinfo_t.get_info(order_id)
                return render_template('orderdish.html',dishes = dishes, orderinfo = order_info, desk_id = desk_id, order_id = order_id)
        else:
            return 'PLEASE LOGIN'
        
@app.route('/showorderinfo', methods = ['POST', 'GET'])
def showorderinfo():
    global desk_id
    db = model('dzf', '123456', '39.108.102.21')
    orderinfo_t = orderinfo(db)
    if request.method == 'GET':
        return render_template('showorderinfo.html')
    if request.method == 'POST':
        if 'desk_id' in request.form:
            desk_id = request.form['desk_id']
            info = orderinfo_t.get_desk_info(desk_id)
            if info:
                return render_template('showorderinfo.html', info = info)
            else:
                error = '桌位号错误！'
                return render_template('showorderinfo.html', error = error)
        elif ('dish_id1' in request.form) and ('quantity1' in request.form):
            order_id = request.form['order_id1']
            dish_id = request.form['dish_id1']
            quantity = request.form['quantity1']
            orderinfo_t.create_info(order_id, dish_id, quantity)
            info = orderinfo_t.get_desk_info(desk_id)
            return render_template('showorderinfo.html', info = info)
        else:
            order_id = request.form['order_id']
            dish_id = request.form['dish_id']
            quantity = request.form['quantity']
            if quantity == '0':
                orderinfo_t.delete_info(order_id, dish_id)
                info = orderinfo_t.get_desk_info(desk_id)
                return render_template('showorderinfo.html', info = info)
            else:
                orderinfo_t.delete_info(order_id, dish_id)
                orderinfo_t.create_info(order_id, dish_id, quantity)
                info = orderinfo_t.get_desk_info(desk_id)
                return render_template('showorderinfo.html', info = info)

@app.route('/checkout', methods = ['GET', 'POST'])
def checkout():
    if request.method == 'GET':
        return render_template('checkout.html')
    if request.method == 'POST':
        global desk_id
        db = model('dzf', '123456', '39.108.102.21')
        orderinfo_t = orderinfo(db)
        order_t = order(db)
        if 'desk_id' in request.form:
            desk_id = request.form['desk_id']
            info = order_t.total_info(desk_id)
            amount = order_t.total_amount(desk_id)[0][0]
            if info:
                return render_template('checkout.html', desk_id = desk_id, info = info, amount = amount)
            else:
                error = '桌位号错误！'
                return render_template('checkout.html', desk_id = desk_id, error = error)
        else:
            if 'paymode' in request.form:
                info = order_t.total_info(desk_id)
                discount = request.form['discount']
                discount = re.sub("\D", "",discount)
                print(discount)
                paymode = request.form['paymode']
                order_id = orderinfo_t.get_desk_info(desk_id)[0][0]
                amount = order_t.total_amount(desk_id)[0][0]
                amount = int(discount)*0.1*int(amount)
                order_t.checkout_order(order_id, discount, paymode)
                return render_template('checkout.html', desk_id = desk_id, info = info, amount = amount, error = '结账成功')
            else:
                order_id = orderinfo_t.get_desk_info(desk_id)[0][0]
                dish_id = request.form['dish_id']
                quantity = request.form['quantity']
                if quantity == 0:
                    orderinfo_t.delete_info(order_id, dish_id)
                else:
                    orderinfo_t.delete_info(order_id, dish_id)
                    orderinfo_t.create_info(order_id, dish_id, quantity)
                amount = order_t.total_amount(desk_id)[0][0]
                info = order_t.total_info(desk_id)
                return render_template('checkout.html', desk_id = desk_id, info = info, amount = amount, error = '修改成功！')


@app.route('/showorders', methods = ['GET', 'POST'])
def showorders():
    db = model('dzf', '123456', '39.108.102.21')
    orderinfo_t = orderinfo(db)
    order_t = order(db)
    if request.method == 'GET':
        orders = order_t.show_all()
        info = orderinfo_t.get_all()
        return render_template('showorders.html', orders = orders, info = info)
    
    if request.method == 'POST':
        order_id = request.form['order_id']
        order_s = order_t.showorder(order_id)
        info = orderinfo_t.get_info(order_id)
        return render_template('showorders.html', orders = order_s, info = info)
    

@app.route('/adddish', methods = ['GET','POST'])
def adddish():
    if request.method == 'GET':
        db = model('dzf', '123456', '39.108.102.21')
        dish_t = dish(db)
        dishes = dish_t.get_dishes()
        db.close()
        return render_template('adddish.html', dishes = dishes)
    
    if request.method == 'POST':
        if 'dish_id1' in request.form:
            db = model('dzf', '123456', '39.108.102.21')
            dish_t = dish(db)
            dish_id = request.form['dish_id1']
            dish_name = request.form['dish_name1']
            dish_price = request.form['dish_price1']
            dish_description = request.form['dish_description1']
            args = [dish_id, dish_name, dish_price, dish_description]
            flag = dish_t.adddish(args)
            dishes = dish_t.get_dishes()
            if flag:
                db.close()
                return render_template('adddish.html', dishes = dishes, error = '添加成功！')
            else:
                db.close()
                return render_template('adddish.html', dishes = dishes, error = '添加失败！')
        else:
            db = model('dzf', '123456', '39.108.102.21')
            dish_t = dish(db)
            dish_id = request.form['dish_id']
            dish_name = request.form['dish_name']
            dish_price = request.form['dish_price']
            dish_description = request.form['dish_description']
            args = [dish_id, dish_name, dish_price, dish_description]
            flag = dish_t.updatedish(args)
            dishes = dish_t.get_dishes()
            if flag:
                db.close()
                return render_template('adddish.html', dishes = dishes, error = '修改成功！')
            else:
                db.close()
                return render_template('adddish.html', dishes = dishes, error = '修改失败！')
            

@app.route('/adddesk', methods = ['GET','POST'])
def adddesk():
    if request.method == 'GET':
        db = model('dzf', '123456', '39.108.102.21')
        desk_t = desk(db)
        desks = desk_t.get_desk()
        db.close()
        return render_template('adddesk.html', desks = desks)
    
    if request.method == 'POST':
        if 'desk_id1' in request.form:
            db = model('dzf', '123456', '39.108.102.21')
            desk_t = desk(db)
            desk_id = request.form['desk_id1']
            desk_maxnum = request.form['desk_maxnum1']
            args = [desk_id, desk_maxnum]
            flag = desk_t.adddesk(args)
            desks = desk_t.get_desk()
            if flag:
                db.close()
                return render_template('adddesk.html', desks = desks, error = '添加成功！')
            else:
                db.close()
                return render_template('adddesk.html', desks = desks, error = '添加失败！')
        else:
            db = model('dzf', '123456', '39.108.102.21')
            desk_t = desk(db)
            desk_id = request.form['desk_id']
            desk_maxnum = request.form['desk_maxnum']
            args = [desk_id, desk_maxnum]
            flag = desk_t.updatedesk(args)
            desks = desk_t.get_desk()
            if flag:
                db.close()
                return render_template('adddesk.html', desks = desks, error = '修改成功！')
            else:
                db.close()
                return render_template('adddesk.html', desks = desks, error = '修改失败！')        
        
        


            
            

            
            
        
            
        

        


    