from flask import Flask,render_template,request,flash,session,redirect,url_for
import mysql.connector
from otp import genotp
from itemid import itemidotp
from cmail import sendmail
import os
# import razorpay
# RAZORPAY_KEY_ID=''
# RAZORPAY_SECRET=''
# client=razorpay.client(auth=(RAZORPAY_KEY _ID,RAZORPAY_SECRET))
mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='ecommerce',
    auth_plugin='mysql_native_password'
)

app = Flask(__name__)
app.secret_key = 'hfbfe78hjefk'

@app.route('/')
def home1():
    return render_template('homepage.html')

@app.route('/reg',methods=['GET','POST'])
def register():
    if request.method=="POST":
        username=request.form['username']
        mobile=request.form['mobile']
        email=request.form['email']
        address=request.form['address']
        password=request.form['password']
        cursor=mydb.cursor()
        cursor.execute('select email from signup')
        data=cursor.fetchall()
        cursor.execute('select mobile from signup')
        edata=cursor.fetchall()
        if(mobile,)in data:
            flash('user already exist')
            return render_template('register.html')
        if(email,)in data:
            flash('Email address already exists')
            return render_template('register.html')
        cursor.close()
        otp=genotp()
        subject='thanks for registering to the application'
        body=f'use this otp to register {otp}'
        sendmail(email,subject,body)
        return render_template('otp.html',otp=otp,username=username,mobile=mobile,email=email,address=address,password=password)
    else:
        return render_template('register.html')

@app.route('/otp/<otp>/<username>/<mobile>/<email>/<address>/<password>',methods=['GET','POST'])
def otp(otp,username,mobile,email,address,password):
    if request.method=="POST":
        uotp=request.form['otp']
        if otp==uotp:
            cursor=mydb.cursor()
            lst=[username,mobile,email,address,password]
            query='insert into signup values(%s,%s,%s,%s,%s)'
            cursor.execute(query,lst)
            mydb.commit()
            cursor.close()
            flash('Details registered')
            return redirect('login')
            #return redirect(url_for('home'))
    else:
        flash('Wrong otp')
        return render_template('otp.html',otp=otp,username=username,mobile=mobile,email=email,address=address,password=password)
    
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=="POST":
        username=request.form['username']
        password=request.form['password']
        cursor=mydb.cursor()
        cursor.execute('select count(*) from signup where username=%s and password=%s',[username,password])
        count=cursor.fetchone()[0]
        print(count)
        if count==0:
            flash('Invalid email or password')
            return render_template('login.html')
        else:
            session['user']=username
            if not session.get(username):
                session[username]={}
            return redirect(url_for('home1'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    if session.get('user'):
        session.pop('user')
        return redirect(url_for('base'))
    else:
        flash('already logged out!')
        return redirect(url_for('login'))


@app.route('/admin')
def admin():
    if 'user' in session:
        cursor=mydb.cursor()
        cursor.execute('select * from signup')
        users=cursor.fetchall()
        cursor.close()
        return render_template('admin.html',users=users)
    else:
        flash('You need to log in first!')
        return redirect('login')
    

@app.route('/adminregister', methods=['GET', 'POST'])
def admin_register():
    if request.method == "POST":
        username = request.form['username']
        mobile = request.form['mobile']
        email = request.form['email']
        address = request.form['address']
        password = request.form['password']
        cursor = mydb.cursor()
        cursor.execute('SELECT email FROM signup')
        email_data = cursor.fetchall()
        cursor.execute('SELECT mobile FROM signup')
        mobile_data = cursor.fetchall()
        if (mobile,) in mobile_data:
            flash('Admin with this mobile number already exists.', 'error')
            return render_template('adminregister.html')
        if (email,) in email_data:
            flash('Admin with this email already exists.', 'error')
            return render_template('adminregister.html')
        cursor.close()
        otp = genotp()
        subject = 'Admin Registration OTP'
        body = f'Use this OTP to complete your registration: {otp}'
        sendmail(email, subject, body)
        return render_template(
            'admin_otp.html', 
            otp=otp, 
            username=username, 
            mobile=mobile, 
            email=email, 
            address=address, 
            password=password
        )
    else:
        return render_template('adminregister.html')
    
@app.route('/adminotp/<otp>/<username>/<mobile>/<email>/<address>/<password>', methods=['GET', 'POST'])
def verify_admin_otp(otp,username,mobile,email,address,password):
    if request.method == "POST":
        entered_otp = request.form['otp']
        if entered_otp == otp:
            cursor = mydb.cursor()
            cursor.execute(
                'INSERT INTO admin (username, mobile, email, address, password) VALUES (%s, %s, %s, %s, %s)',
                (username,mobile,email,address,password)
            )
            mydb.commit()
            cursor.close()
            flash('Admin registration successful!', 'success')
            return redirect(url_for('adminlogin'))
        else:
            flash('Invalid OTP. Please try again.', 'error')
            return render_template(
                'admin_otp.html', 
                otp=otp, 
                username=username, 
                mobile=mobile, 
                email=email, 
                address=address, 
                password=password
            )
    return render_template('adminotp.html', otp=otp)

@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form['password']
        cursor = mydb.cursor()
        cursor.execute('select count(*) from signup where email=%s and password=%s', [email,password])
        count = cursor.fetchone()[0] 
        if count == 0:
            flash('Inval  id admin username or password', 'error')
            return render_template('adminlogin.html')
        else:
            session['admin'] = email
            flash('Admin login successful!', 'success')
            return redirect(url_for('admindashboard'))  

    return render_template('adminlogin.html')

@app.route('/adminlogout')
def adminlogout():
    if session.get('admin'):
        session.pop('admin') 
        flash('Successfully logged out as admin!', 'success')
        return redirect(url_for('adminlogin'))
    else:
        flash('You are already logged out!', 'info')
        return redirect(url_for('adminlogin'))


@app.route('/additems',methods=['GET','POST']) 
def additems():
    if session.get('admin'):
        if request.method=="POST":  
            name=request.form['name']
            description=request.form['desc']
            quantity=request.form['qty']
            category=request.form['category']
            price=request.form['price']
            image=request.files['image']
            valid_categories=['electronics','grocery','fashion','home']
            if category not in valid_categories:
                flash('Invalid category.Please select a valid option.')
                return render_template('items.html')
            cursor=mydb.cursor()
            idotp=itemidotp()
            filename=idotp+'.jpg'
            cursor.execute('insert into additems(itemid,name,discription,qty,category,price) values(%s,%s,%s,%s,%s,%s)',[idotp,name,description,quantity,category,price])
            mydb.commit()
            path=os.path.dirname(os.path.abspath(_file_))
            static_path=os.path.join(path,'static')
            image.save(os.path.join(static_path,filename))
            flash('Item added succesfully!')
    return render_template('item.html')

@app.route('/addcart/<itemid>/<name>/<category>/<price>/<quantity>', methods=['GET', 'POST'])
def addcart(itemid,name,category,price,quantity):
    if not session.get('user'):
        return redirect(url_for('login'))
    else:
        print(session)
        if itemid not in session.get(session['user'],{}):
            if session.get(session['user']) is None:
                session[session['user']]={}
            session[session['user']][itemid]=[name,price,1,f'{itemid}.jpg',category]
            session.modified=True
            flash(f'{name}added to cart')
            return '<h2>quantity increases in the cart</h2>'
        session[session['user']][itemid][2]+=1
        session.modified=True
        flash(f'{name} quantity increased in the cart')
        return '<h2>quantity increases in the cart</h2>'
    
@app.route('/cartpop/<itemid>')
def cartpop(itemid):
    print(itemid)
    if session.get('user'):
        print(session)
        session[session.get('user')].pop(itemid)
        session.modified=True
        flash("item removed")
        print(session)
        return redirect(url_for('viewcart'))
    else:
        return redirect(url_for('login'))

@app.route('/viewcart')
def viewcart():
    if not session.get('user'):
        return redirect(url_for('login'))
    user_cart=session.get(session.get('user'))#retrive the card items from the session
    if not user_cart:
        items='empty'
    else:
        items=user_cart #fetch the items from the session
    if items=='empty':
        return '<h3> Your cart is empty </h3>'
    return render_template('cart.html',items=items)


@app.route('/dashboardpage')
def dashboardpage():  # Only one definition of this route
    cursor = mydb.cursor()
    cursor.execute("select * from additems")
    items = cursor.fetchall()
    return render_template('dashboard.html', items=items)

@app.route('/status')
def status():
    cursor = mydb.cursor()
    cursor.execute('select * from additems')
    items = cursor.fetchall()
    return render_template('statics.html', items=items)

@app.route('/updateproducts/<itemid>', methods=['GET', 'POST'])
def updateproducts(itemid):
    if session.get('admin'):
        print(itemid)
        cursor = mydb.cursor()
        cursor.execute('select name, discription, qty, category, price from additems where itemid=%s', [itemid])
        items = cursor.fetchone()
        if request.method == 'POST':
            name = request.form['name']
            discription = request.form['desc']
            quantity = request.form['qty']
            category = request.form['category']
            price = request.form['price']
            cursor=mydb.cursor()
            cursor.execute('update additems set name=%s, discription=%s, qty=%s, category=%s, price=%s where itemid=%s',
            [name, discription, quantity, category, price, itemid])
            mydb.commit()
            cursor.close()
            #flash('Item updated successfully')
            return redirect(url_for('dashboardpage'))
        return render_template('updateproducts.html', items=items)
    else:
        return redirect(url_for('adminlogin'))

@app.route('/deleteproducts/<itemid>')
def deleteproducts(itemid):
    cursor=mydb.cursor()
    cursor.execute('delete from additems where itemid=%s',[itemid])
    mydb.commit()
    cursor.close()
    path=os.path.dirname(os.path.abspath(_file_))
    static_path=os.path.join(path,'static')
    filename=itemid+'.jpg'
    os.remove(os.path.join(static_path,filename))
    flash('deleted')
    return redirect(url_for('status'))

@app.route('/dis/<itemid>')
def dis(itemid):
    cursor=mydb.cursor()
    cursor.execute('select * from additems where itemid=%s',[itemid])
    items=cursor.fetchone()
    return render_template('display.html',items=items)
def category(category):
    if session.get('user'):
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select * from additems where category=%s',[category])
        data=cursor.fetchall()
        cursor.close()
        return render_template('categories.html',data=data)
    else:
        return redirect(url_for('login'))

    
 
@app.route('/contact', methods=['GET','POST'])
def contact():
    if request.method=='POST':
        name=request.form['name']
        email=request.form['email']
        message=request.form['message']
        cursor=mydb.cursor()
        cursor.execute("insert into contacts(name, email, meassgae) values (%s, %s, %s)", (name, email, message))
        mydb.commit()
        cursor.close()
        flash("your message has beeb sent successfully!")
        return redirect(url_for('home1'))
    return render_template('contact.html')


#for payment---->id,name,price
@app.route('/pay/<itemid>/<name>/<price>',methods=['GET','POST'])
def pay(itemid,name,price):
    try:
        #Get the quantity from the form
        qyt=int(request.form['qyt'])

        #Caluculate the total amount in paise (price is in rupees) 
        total_price = int(price)*qyt # Ensure integer multiplication 
        
        print(f"creating payment for item ID:{itemid}, Name:{name}, Total Price:{total_price}")

        #create Razorpay order
        order = client.order.create({
            'amount':total_price,
            'currency':'INR',
            'payment_capture':'1'
        })
        print(f'order created:{order}')
        return render_template('pay.html',order=order,itemid=itemid,name=name,price=total_price,qyt=qyt)
    except Exeception as e:
        #Log the error and retrun a 400 response
        print(f'Error creating order:{str(e)}')
        return str(e),400

@app.route('/orders')
def orders():
    if session.get('user'):
    cursor= mydb.cursor(buffered=True)
    cursor.execute('select *from orders where user=%s',[user])
    data=cursor.fetchall()
    cursor.close()
    return render_template('orderdisplay.html',data=data)
else:
    return redirect(url_for('login'))



@app.rotute('/success',methods=['POST'])
def success():
    payment_id=request.form.get('razorpay_payment_id')
    order_id=request.form.get('razorpay_order_id')
    signature=request.form.get('razorpay_signature')
    name=request.form.get('name')
    itemid=request.form.get('itemid')
    total_price=request.form.get('total_price')
    qyt=request.form.get('qyt')
    

    #verification process
    params_dict={
        'razorpay_order_id':order_id, 
        'razorpay_payment_id':payment_id,
        'razorpay_signature':signature
    }
    try:
        client.utility.verify_payment_signature(params_dict)
        cursor=mydb.cursor(buffered=True)
        cursor.excute('insert into orders(itemid,item_name,total_price,user,qyt)values(%s,%s,%s,%s,%s)',
        [itemid,name,total_price,session.get('user'),qyt])
        mydb.commit()
        cursor.close()
        flash('Order placed successfully')
        return 'orders'
@app.route('/search',methods=['GET','POST'])
def search():
    if request.method=='POST':
        name=request.from['search']
        print(name)
        cursor=mydb.cursor()
        cursor.execute('select *from additems where name =%s',['name'])
        data=cursor.fetchall()
        return render render_template('dashboard.html',items=data)
if __name__ =='__main__':
    app.run(debug=True)
 