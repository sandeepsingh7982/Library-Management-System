from flask import Flask, render_template, request,redirect,session
import sqlite3 as sql
import os


app=Flask(__name__)
app.secret_key=os.urandom(24)


@app.before_first_request
def before():
        database='library.db'
        with sql.connect(database) as conn:
                cursor=conn.cursor()
                query='CREATE TABLE IF NOT EXISTS add_books(sno integer primary key AUTOINCREMENT , book_id integer, book_name text[60]) '
                cursor.execute(query)
                query1='create table IF NOT EXISTS issue_books(student_id integer primary key,student_name text[100],books text[200],return_books text[200]) '
                cursor.execute(query1)
                query2='create table IF NOT EXISTS reg_form(email text[100],password text[100]) '
                cursor.execute(query2)
                query3='CREATE TABLE IF NOT EXISTS users(user_id integer primary key AUTOINCREMENT,name text[50],email text[50],password varchar[50])'
                cursor.execute(query3)
                

@app.route('/',methods=['GET','POST'])
def login():
    if(request.method=='POST'):
        data=dict(request.form)
        values=list(data.values())
        with sql.connect('library.db') as conn:
            cursor=conn.cursor()
            query='select * from users where email=? and password=?'
            cursor.execute(query,values)
            user=cursor.fetchall()
            if len(user)>0:
                session['user_id']=user[0][0]
                session['user_name']=user[0][1].upper()
                return redirect('/home')
            else:
                return redirect('/')   
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if(request.method=='POST'):
        data=dict(request.form)
        values=list(data.values())
        with sql.connect('library.db') as conn:
            cursor=conn.cursor()
            query='INSERT INTO users(name,email,password) values(?,?,?)'
            cursor.execute(query,values)
            conn.commit()
        return redirect('/')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/home')
def home():
    if 'user_id' in session:
        return render_template('home.html',s=session)
    else:
        return redirect('/')

@app.route('/add',methods=['GET','POST'])
def add():
    if 'user_id' in session:
        if (request.method=='POST'):
            data=dict(request.form)
            values=list(data.values())
            with sql.connect('library.db') as conn:
                cursor=conn.cursor()
                query=f'INSERT INTO add_books(book_id,book_name) values(?,?)'
                cursor.execute(query,values)
                conn.commit()
            return render_template('add.html',s=session)
        return render_template('add.html',s=session)
    else:
        return redirect('/')

@app.route('/available')
def show():
    if 'user_id' in session:
        with sql.connect('library.db') as conn:
            cursor=conn.cursor()
            cursor.execute("select * from add_books")
            data=cursor.fetchall()
        return render_template('available.html',d=data,s=session)
    else:
        return redirect('/')

@app.route('/student')
def student():
    if 'user_id' in session:
        with sql.connect('library.db') as conn:
            cursor=conn.cursor()
            cursor.execute("select * from issue_books")
            data=cursor.fetchall()
        return render_template('student.html',s=data,d=session)
    else:
        return redirect('/')

@app.route('/issue')
def get():
    if 'user_id' in session:
        with sql.connect('library.db') as conn:
            cursor=conn.cursor()
            cursor.execute("select * from add_books")
            data=cursor.fetchall()
            l=[]
            for i in data:
                l.append(i[2])
            return render_template('issue.html',d=l,s=session)
    else:
        return redirect('/')

@app.route('/issue',methods=['GET','POST'])
def issue():
    if 'user_id' in session:
        if (request.method=='POST'):
            data=dict(request.form)
            values=list(data.values())
            with sql.connect('library.db') as conn:
                cursor=conn.cursor()
                query=f'INSERT INTO issue_books(student_id,student_name,books,return_books) values(?,?,?,?)'
                cursor.execute(query,values)
                conn.commit()
            return render_template('issue.html')
        return render_template('issue.html')
    else:
        return redirect('/')
    
@app.route('/deletebyid/<int:sno>')
def deletebyid(sno):
    if 'user_id' in session:
        with sql.connect('library.db') as conn:
            query='delete from add_books where sno=?;'
            conn.execute(query,(sno,))
            conn.commit()
        return redirect('/available')
    else:
        return redirect('/')

@app.route('/deletebystudentid/<int:sno>')
def deletebystudentid(sno):
    if 'user_id' in session:
        with sql.connect('library.db') as conn:
            query='delete from issue_books where student_id=?;'
            conn.execute(query,(sno,))
            conn.commit()
        return redirect('/student')
    else:
        return redirect('/')

@app.route('/update',methods=['GET','POST'])
def updatestudentdetail():
    if 'user_id' in session:
        if request.method=='POST':
            data=dict(request.form)
            values=list(data.values())
            temp=[]
            temp.append(values[1]) 
            temp.append(values[2]) 
            temp.append(values[3]) 
            temp.append(values[0]) 
            query='''UPDATE issue_books
                    SET student_name=?,
                    books=?,
                    return_books=?
                    WHERE student_id=?;'''
            with sql.connect('library.db') as conn:
                cursor=conn.cursor()
                cursor.execute(query,temp)
                conn.commit()
                return render_template('update.html')
        return render_template('update.html')
    else:
        return redirect('/')

@app.route('/fetch/<string:book_name>')
def fetch(book_name):
    if 'user_id' in session:
        value=book_name
        return render_template('issue.html',d=value)
    else:
        return redirect('/')

       

if __name__=='__main__':    
    app.run(debug=True)