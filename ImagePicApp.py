
from re import M
import sqlite3
from flask import Flask, redirect,render_template,request,g,url_for
import matplotlib.pyplot as plt
from PIL import Image
from flask_paginate import Pagination, get_page_parameter
import os

app = Flask(__name__, static_folder="./templates/kabegami")

def get_db():
    if 'db' not in g:
        # データベースをオープンしてFlaskのグローバル変数に保存
        g.db = sqlite3.connect('images.db')
    return g.db

@app.route('/')
def index():

    # データベースを開く
    con = get_db()

    cur = con.execute("select count(*) from sqlite_master where TYPE='table' AND name='Images'")

    for row in cur:
        if row[0] == 0:
            cur.execute("CREATE TABLE Images(id INTEGER PRIMARY KEY, image_path STRING, image_keyword STRING)")

            con.commit()
    
    cur = con.execute("select * from Images order by id")
    data = cur.fetchall()
    con.close()

    
    page = request.args.get(get_page_parameter(), type=int, default=1)
    res = data[(page - 1)*12: page*12]
    pagination = Pagination(page=page, total=len(data),  per_page=12, css_framework='bootstrap4')


    return render_template('list_index.html', data = res, pagination=pagination)

@app.route('/lists')
def index_lost():

    # データベースを開く
    con = get_db()

    cur = con.execute("select count(*) from sqlite_master where TYPE='table' AND name='Images'")

    for row in cur:
        if row[0] == 0:
            cur.execute("CREATE TABLE Images(id INTEGER PRIMARY KEY, image_path STRING, image_keyword STRING)")
            
            con.commit()
    
    cur = con.execute("select * from Images order by id")
    data = cur.fetchall()
    con.close()

    page = request.args.get(get_page_parameter(), type=int, default=1)
    res = data[(page - 1)*12: page*12]
    pagination = Pagination(page=page, total=len(data),  per_page=12, css_framework='bootstrap4')


    return render_template('list_index.html', data = res, pagination=pagination)

@app.route('/result', methods=["GET", "POST"])
def result_post():

    file = request.files['example']
    file.save(os.path.join('templates/kabegami', file.filename))
    name = file.filename

    # データベースを開く
    con = get_db()

    cur = con.execute("select MAX(id) AS max_code from Images")

    cur2 = con.execute("select * from Images order by id")
    data2 = cur2.fetchall()
    list = []
    for item in data2:
        list.append(item[2])
    
    list2 = []
    for item in list:
        l = item.split(',')
        list2 = list2 + l
    list3 = []
    for i in list2:
        if i not in list3:
            list3.append(i)

    new_list = sorted(list3)

    for row in cur:
        if row[0] != None:
            new_code = row[0] + 1
        else:
            new_code = 1
    cur.close()
    sql = "INSERT INTO Images(id, image_path, image_keyword)values({},'{}','_?/keyword/?_')".format(new_code, name)
    con.execute(sql)
    con.commit()

    cur = con.execute("select * from Images where id = {}".format(new_code))
    data = cur.fetchall()
    con.close()
    
    return render_template('register.html', data = data, list=new_list)

@app.route("/register", methods=["POST"])
def register():
    
    con = get_db()
    sql3 = "select * from Images where image_keyword LIKE '%_?/keyword/?_%'"
    #cur = con.execute("select *  from Images where id = MAX(id)")
    cur = con.execute(sql3)
    data = cur.fetchall()
    
    
    data1 = data[0][0]
    data1_ = int(data1)
    data2 = data[0][1]
    data2_ = str(data2)
   
    new_key = request.form.get("key")

    sql2 = "DELETE FROM Images WHERE image_keyword LIKE '%_?/keyword/?_%'"
    con.execute(sql2)
    con.commit()
   
    sql4 = "insert into Images(id, image_path, image_keyword) values({}, '{}', '{}')".format(data1_, data2_, new_key)
    con.execute(sql4)
    con.commit()
    cur = con.execute("select * from Images order by id")
    data = cur.fetchall()
    
    con.close()

    page = request.args.get(get_page_parameter(), type=int, default=1)
    res = data[(page - 1)*12: page*12]
    pagination = Pagination(page=page, total=len(data),  per_page=12, css_framework='bootstrap4')


    render_template('list_index.html', data = res, pagination=pagination)
    return redirect("/lists")



@app.route("/delete/<int:id>", methods=["GET"])
def delete_post(id):

    con = get_db()

    sql2 = "DELETE FROM Images WHERE id = {}".format(id)
    con.execute(sql2)
    con.commit()

    cur = con.execute("select * from Images order by id")
    data = cur.fetchall()
    con.close()
    page = request.args.get(get_page_parameter(), type=int, default=1)
    res = data[(page - 1)*12: page*12]
    pagination = Pagination(page=page, total=len(data),  per_page=12, css_framework='bootstrap4')

    render_template('list_index.html', data = res, pagination=pagination)
    return redirect("/lists")

@app.route("/open_image/<int:id>")
def open_image(id):
    con = get_db()
    sql = "select image_path from Images where id={}".format(id)
    cur = con.execute(sql)
    image = cur.fetchall()
    con.close()

    image2 = str(image)
    
    # PIL.Imageで画像を開く
    pic = image2.strip("[")
    pic2 = pic.strip("]")
    pic3 = pic2.strip("(")
    pic4 = pic3.strip(")")
    pic5 = pic4.strip(",")
    pic6 = pic5.strip("'")
    
    path = "templates/kabegami/{}".format(pic6)
    
    img = Image.open(path)
    # OS標準の画像ビューアで表示
    img.show()
    
    return redirect("/")

@app.route("/row_image", methods=["POST"])
def row_image():
    im = request.form["check"]
    con = get_db()
    cur = con.execute("select * from Images where image_keyword LIKE '%{}%'".format(im))
    data = cur.fetchall() 
    
    con.close()
    
    return render_template("images.html", data=data)

@app.route("/result2")
def open_image2():
    con = get_db()

    cur = con.execute("select * from Images order by id")
    data = cur.fetchall()
    con.close()
    list = []
    for item in data:
        list.append(item[2])
    
    list2 = []
    for item in list:
        l = item.split(',')
        list2 = list2 + l
    list3 = []
    for i in list2:
        if i not in list3:
            list3.append(i)

    new_list = sorted(list3)
    
    return render_template('index_image.html', data=data, list=new_list)

    
@app.route("/list")
def list_open():
    con = get_db()
    cur = con.execute("select * from Images order by id")
    data = cur.fetchall()
    con.close()

    page = request.args.get(get_page_parameter(), type=int, default=1)
    res = data[(page - 1)*12: page*12]
    pagination = Pagination(page=page, total=len(data),  per_page=12, css_framework='bootstrap4')

    return render_template('list_index.html', data = res, pagination=pagination)

@app.route("/update/<int:id>")
def update(id):
    con = get_db()
    sql3 = "select * from Images where id = {}".format(id)
    
    cur = con.execute(sql3)
    data = cur.fetchall()
    con.close()
    
    return render_template('update.html', data = data)
    
    
@app.route("/update/<int:id>", methods=["POST"])
def update_post(id):
    con = get_db()
    sql3 = "select * from Images where id = {}".format(id)
    cur = con.execute(sql3)
    data = cur.fetchall()
    
    
    data1 = data[0][0]
    data1_ = int(data1)
    data2 = data[0][1]
    data2_ = str(data2)
   
    new_key = request.form.get("key_word")

    sql2 = "DELETE FROM Images WHERE id = {}".format(id)
    con.execute(sql2)
    con.commit()
   
    sql4 = "insert into Images(id, image_path, image_keyword) values({}, '{}', '{}')".format(data1_, data2_, new_key)
    con.execute(sql4)
    con.commit()
    cur = con.execute("select * from Images order by id")
    data = cur.fetchall()
    
    con.close()
    
    return redirect("/list")

@app.route("/about_index")
def about():
    return render_template('about_index.html')


if __name__ == '__main__':
    app.debug = True
    app.run(host='localhost')
