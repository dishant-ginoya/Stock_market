from flask import Flask, render_template, request, session, redirect , jsonify, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import os
import yfinance as yf
import mplfinance as mpf
import random
import smtplib
from email.message import EmailMessage
import ssl



app=Flask(__name__)
app.secret_key = os.urandom(24)

class DataStore():
    login_otp = ""
    login_email = ""
    regi_email = ""
    regi_name = ""

info = DataStore()


@app.route('/')
def base():
    return render_template('log_in.html')


@app.route('/send_otp', methods=['POST','GET'])
def send_otp():
    if info.login_email != None:
        context = ssl.create_default_context()
        smtp = smtplib.SMTP_SSL('smtp.gmail.com',465, context=context)
        sender = "develofmyworld@gmail.com"
        receiver = info.login_email
        subject = "Aapna stock Login"
        number = ''.join([str(random.randint(0,9)) for i in range(4)])
        info.login_otp = number
        print(number)
        body = """
hello,
    use the verification code below to log in.
    """+str(number)+"""

    Do not share this OTP with anyone. Aapna stock takes your account security very seriously.
    you received thid email because you requested to log in to your account. if you didn`t request to log in, you can safely ignore this email.

    Thank you !

Aapna stock
"""
        smtp.login(sender,'jwzyzzafsotyaemu')
        em = EmailMessage()
        em['From'] = sender
        em['To'] = receiver
        em['Subject'] = subject
        em.set_content(body)
        smtp.sendmail(sender, receiver, em.as_string())
        smtp.quit()
        return redirect(url_for('otp'))
    else:
        return redirect(url_for('base'))


@app.route('/verify_otp', methods=['POST','GET'])
def otp():
    conn = mysql.connector.connect(host="sql899.main-hosting.eu", user="u993197072_stock_market", password="Stock_market2023", database="u993197072_Stock_market")
    cur = conn.cursor()
    cur.execute(""" SELECT * FROM user_info WHERE email_add = '{}' """.format(info.login_email))
    users = cur.fetchall()
    if users:
        user_id = users[0][1]

        return render_template('otp.html', user_id = user_id)
    else:
        return redirect(url_for('base'))

  
@app.route('/verify', methods=['POST','GET'])  
def verify_otp():
    conn = mysql.connector.connect(host="sql899.main-hosting.eu", user="u993197072_stock_market", password="Stock_market2023", database="u993197072_Stock_market")
    cur = conn.cursor()
    if request.method == 'POST':
        con_otp = request.form.get('otp')
        if info.login_otp == con_otp:  
            cur.execute(""" SELECT * FROM user_info WHERE email_add = '{}' """.format(info.login_email))
            users = cur.fetchall()
            session['user_id'] = users[:]
            return redirect('/home')
        else:
            a = ("<script type='text/javascript'>alert('Please enter valid otp ...');window.location.href='/verify_otp'</script>")
        return (a)
    else:
        return redirect(url_for('base'))


@app.route('/registration')
def registration():
    return render_template('registration.html')


@app.route('/term_condition')
def term_condition():
    return render_template('term_condition.html')


@app.route('/home', methods=['POST','GET'])
def home():
    conn = mysql.connector.connect(host="sql899.main-hosting.eu", user="u993197072_stock_market", password="Stock_market2023", database="u993197072_Stock_market")
    cur = conn.cursor()
    if 'user_id' in session:
        cur.execute(""" SELECT * FROM company """)
        data = cur.fetchall()
        return render_template('home.html', data=data)
    else:
        return redirect(url_for('base'))


@app.route('/profile')
def profile():
    if 'user_id' in session:
        return render_template('profile.html', user_id = session['user_id'])
    else:
        return redirect(url_for('base'))


@app.route('/dashboard', methods=['POST','GET'])
def dashboard():
    conn = mysql.connector.connect(host="sql899.main-hosting.eu", user="u993197072_stock_market", password="Stock_market2023", database="u993197072_Stock_market")
    cur = conn.cursor()
    if 'user_id' in session:
        user_id = session['user_id'][0][1]
        buy = "buy"
        sell = "sell"
        sell_comapny = ""
        if conn:
            available = []
            cur.execute(""" SELECT DISTINCT company_name FROM `buy&sell` WHERE user_id = '{}' ORDER BY company_name ASC """.format(user_id))
            res = cur.fetchall()
            for x in res:
                y=x[:1]
                sep = ''.join(y)

                cur.execute(""" SELECT company_name,sum(qty),price FROM `buy&sell` WHERE `buy&sell` = '{}' && `company_name` = '{}' && user_id = '{}' """.format(buy, sep, user_id))
                abc = cur.fetchall()
                for x in abc:
                    if x != (None,None,None):
                        buy_comapny = abc[0][0]
                        buy_qty = float(abc[0][1])
                        buy_price = float(abc[0][2])

                        cur.execute(""" SELECT company_name,sum(qty),price FROM `buy&sell` WHERE `buy&sell` = '{}' && `company_name` = '{}' && user_id = '{}' """.format(sell, sep, user_id))
                        abc1 = cur.fetchall()
                        for x1 in abc1:
                            if x1 != (None,None,None):
                                sell_comapny = abc1[0][0]
                                sell_qty = float(abc1[0][1])
                                sell_price = float(abc1[0][2])

                                if (buy_comapny) == (sell_comapny):
                                    finall_qty1 = int(buy_qty) - int(sell_qty)
                                    finall_price1 = float(sell_price) * float(finall_qty1)
                                    available.append([sell_comapny, finall_qty1, sell_price, finall_price1])
                            else:
                                pass
                            if (buy_comapny) != (sell_comapny):
                                finall_qty = buy_qty - 0
                                finall_price = float(buy_price) * float(buy_qty)
                                available.append([buy_comapny, finall_qty, buy_price, finall_price])
                    else:
                        pass
        return render_template('dashboard.html', available = available)
    else:
        return redirect(url_for('base'))


@app.route('/holding')
def holding():
    conn = mysql.connector.connect(host="sql899.main-hosting.eu", user="u993197072_stock_market", password="Stock_market2023", database="u993197072_Stock_market")
    cur = conn.cursor()
    if 'user_id' in session:
        user_id = session['user_id'][0][1]
        cur.execute(""" SELECT * FROM `add_company` WHERE user_id = '{}' ORDER BY company_name ASC """.format(user_id))
        res = cur.fetchall()
        return render_template('holding.html', res = res, user_id = session['user_id'])
    else:
        return redirect(url_for('base'))


@app.route('/position', methods=['POST','GET'])
def position():
    conn = mysql.connector.connect(host="sql899.main-hosting.eu", user="u993197072_stock_market", password="Stock_market2023", database="u993197072_Stock_market")
    cur = conn.cursor()
    if 'user_id' in session:
        user_id = session['user_id'][0][1]
        cur.execute(""" SELECT c.name, c.open, c.high, c.low, c.close, b.`buy&sell`, b.qty, b.price, b.total FROM `buy&sell` b INNER JOIN company c ON b.company_name = c.name WHERE b.user_id = '{}' ORDER BY `date&time` DESC """.format(user_id))
        res = cur.fetchall()
    return render_template('position.html', user_id = session['user_id'],res = res)


@app.route('/fund',methods=['POST','GET'])
def fund():
    conn = mysql.connector.connect(host="sql899.main-hosting.eu", user="u993197072_stock_market", password="Stock_market2023", database="u993197072_Stock_market")
    cur = conn.cursor()
    if 'user_id' in session:
        user_id = session['user_id'][0][1]
        cur.execute(""" SELECT closing_balance FROM closing_balance WHERE user_id = '{}' """.format(user_id))
        closing_balance = cur.fetchone()
        return render_template('fund.html', amount = closing_balance, user_id = session['user_id'])
    else:
        return redirect(url_for('base'))


@app.route('/search',methods=['POST','GET'])
def search():
    conn = mysql.connector.connect(host="sql899.main-hosting.eu", user="u993197072_stock_market", password="Stock_market2023", database="u993197072_Stock_market")
    cur = conn.cursor()
    if request.method == 'POST':
        search_word = request.form['query']
        if search_word != '':
            cur.execute(""" SELECT * FROM company WHERE name LIKE '%{}%' """.format(search_word))
            data = cur.fetchall()
        return jsonify({'htmlresponse': render_template('search_data.html',data=data)})
    return redirect(url_for('home'))


@app.route('/buy/<string:id>', methods=["POST", "GET"])
def buy(id):
    conn = mysql.connector.connect(host="sql899.main-hosting.eu", user="u993197072_stock_market", password="Stock_market2023", database="u993197072_Stock_market")
    cur = conn.cursor()
    if conn:
        opening_share = 1000
        buy = "buy"
        sell = "sell"
        cur.execute(""" SELECT sum(qty) AS available FROM `buy&sell` WHERE `buy&sell` ='{}' && company_name='{}' """.format(buy, id))
        res1 = cur.fetchone()
        for x in res1:
            if x == None:
                x = 0
            else:
                x = x
        cur.execute(""" SELECT sum(qty) AS available FROM `buy&sell` WHERE `buy&sell` ='{}' && company_name='{}' """.format(sell, id))
        res = cur.fetchone()
        for y in res:
            if y == None:
                y = 0
            else:
                y = y
        available_share = str(opening_share - x + y)
        if 'user_id' in session:
            cur.execute(""" SELECT * FROM company WHERE name = '{}' """.format(id))
            res = cur.fetchall()
    return render_template('buy.html', company = res, user_id = session['user_id'], available = available_share)


@app.route('/sell/<string:id>', methods=["POST", "GET"])
def sell(id):
    conn = mysql.connector.connect(host="sql899.main-hosting.eu", user="u993197072_stock_market", password="Stock_market2023", database="u993197072_Stock_market")
    cur = conn.cursor()
    if 'user_id' in session:
        user_id = session['user_id'][0][1]
        if conn:
            buy = "buy"
            sell = "sell"
            cur.execute(""" SELECT sum(qty) AS available FROM `buy&sell` WHERE `buy&sell` ='{}' && company_name='{}' && user_id = '{}' """.format(buy, id, user_id))
            res1 = cur.fetchone()
            for x in res1:
                if x == None:
                    x = 0
                else:
                    x = x
            cur.execute(""" SELECT sum(qty) AS available FROM `buy&sell` WHERE `buy&sell` ='{}' && company_name='{}'&& user_id = '{}' """.format(sell, id, user_id))
            res = cur.fetchone()
            for y in res:
                if y == None:
                    y = 0
                else:
                    y = y
            available_share = str(x - y)
            cur.execute(""" SELECT * FROM company WHERE name = '{}' """.format(id))
            res = cur.fetchall()
    return render_template('sell.html', company=res, user_id=session['user_id'], available=available_share)


@app.route('/chart/<string:id>', methods=["POST", "GET"])
def chart(id):
    name = (str(id) + str(".NS"))
    df = yf.Ticker(name).history(period="max")
    mc = mpf.make_marketcolors(
    up='g',down='r',
    edge={"up":"g","down":"r"}
    )
    style = mpf.make_mpf_style(marketcolors=mc)
    df = df.loc["2022-12-1":]
    mpf.plot(df, type="candle", title=id, style=style, ylabel="Price (Rs)" , xlabel="Jan - Dec\n(2022)")
    return redirect(url_for('home'))


@app.route('/holding_chart/<string:id>', methods=["POST", "GET"])
def holding_chart(id):
    name = (str(id) + str(".NS"))
    df = yf.Ticker(name).history(period="max")
    mc = mpf.make_marketcolors(
    up='g',down='r',
    edge={"up":"g","down":"r"}
    )
    style = mpf.make_mpf_style(marketcolors=mc)
    df = df.loc["2022-12-1":]
    mpf.plot(df, type="candle", title=id, style=style, ylabel="Price (Rs)" , xlabel="Jan - Dec\n(2022)")
    return redirect(url_for('holding'))


@app.route('/add/<string:id>', methods=["POST", "GET"])
def add(id):
    conn = mysql.connector.connect(host="sql899.main-hosting.eu", user="u993197072_stock_market", password="Stock_market2023", database="u993197072_Stock_market")
    cur = conn.cursor()
    if 'user_id' in session:
        user_id = session['user_id'][0][1]
        if conn:
            cur.execute(""" SELECT * FROM company WHERE name = '{}' """.format(id))
            res = cur.fetchall()
            company_name = res[0][1]
            price = res[0][2]
            high = res[0][3]
            low = res[0][4]
            close = res[0][5]

            if res:
                cur.execute(""" SELECT * FROM `add_company` WHERE user_id = '{}' && company_name = '{}' """.format(user_id, company_name))
                sql = cur.fetchall()
                if not sql:
                    cur.execute(""" INSERT INTO `add_company`(id, user_id, company_name, open, high, low, close) VALUES (NULL,'{}','{}','{}','{}','{}','{}') """.format(user_id, company_name, price, high, low, close))
                    conn.commit()
                    a = ("<script type='text/javascript'>alert('Successfully add company to holding...');window.location.href='/home'</script>")
                    return (a)
                else:
                    a = ("<script type='text/javascript'>alert('This company is already taken...');window.location.href='/home'</script>")
                    return (a)
        else:
            a = ("<script type='text/javascript'>alert('Not add company to holding...');window.location.href='/home'</script>")
        return (a)
    else:
        return redirect(url_for('base'))


@app.route('/delete/<string:id>', methods=["POST", "GET"])
def delete(id):
    conn = mysql.connector.connect(host="sql899.main-hosting.eu", user="u993197072_stock_market", password="Stock_market2023", database="u993197072_Stock_market")
    cur = conn.cursor()
    if 'user_id' in session:
        user_id = session['user_id'][0][1]
        cur.execute(""" DELETE FROM add_company WHERE user_id = '{}' && company_name = '{}' """.format(user_id, id))
        conn.commit()
        a = ("<script type='text/javascript'>alert('Remove Successfully...');window.location.href='/holding'</script>")
        return (a)


@app.route('/login', methods=['POST','GET'])
def login():
    conn = mysql.connector.connect(host="sql899.main-hosting.eu", user="u993197072_stock_market", password="Stock_market2023", database="u993197072_Stock_market")
    cur = conn.cursor()
    if request.method == 'POST':
        l_email = request.form.get('email')
        l_password = request.form.get('password')

        cur.execute(""" SELECT * FROM user_info WHERE email_add = '{}' """.format(l_email))
        users = cur.fetchall()
        if users:
            if check_password_hash(users[0][2], l_password):
                info.login_email = l_email
                return redirect(url_for('send_otp'))
            else:
                a = ("<script type='text/javascript'>alert('Incorrect password !...');window.location.href='/'</script>")
                return (a)
        else:
            a = ("<script type='text/javascript'>alert('Please enter register email !...');window.location.href='/'</script>")
            return (a)
    else:
        return redirect(url_for('base'))


@app.route('/reg', methods=['POST','GET'])
def sing_up():
    conn = mysql.connector.connect(host="sql899.main-hosting.eu", user="u993197072_stock_market", password="Stock_market2023", database="u993197072_Stock_market")
    cur = conn.cursor()
    if request.method == 'POST':

        cur.execute(""" SELECT * FROM user_info """)
        cur.fetchall()

        f_name = request.form.get('f_name')
        m_name = request.form.get('m_name')
        l_name = request.form.get('l_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        pan_num = request.form.get('pan_num')
        bank_name = request.form.get('bank_name')
        ifsc_code = request.form.get('ifsc_code')
        acc_num = request.form.get('acc_num')
        dp_no = request.form.get("dp_no")
        bo_no = request.form.get("bo_no")
        password = request.form.get('password')
        country = request.form.get('country')
        state = request.form.get('state')
        city = request.form.get('city')

        info.regi_email = email
        info.regi_name = m_name

        hash_password = generate_password_hash(password)

        cur.execute(""" SELECT * FROM user_info WHERE email_add = '{}' """.format(email))
        sql = cur.fetchall()
        if not sql:
            cur.execute(""" SELECT * FROM user_info """)
            cur.fetchall()

            demate = (str(dp_no) + str(bo_no))

            char = m_name[:1] + l_name[:1]
            f_char = char.upper()

            num = str("0000") + str(cur.rowcount + 1)
            f_num = num[-4:]

            user_id = f_char + f_num

            cur.execute(""" INSERT INTO user_info (id, user_id, password, first_name, middle_name, last_name, email_add, phone_no, pan_card, bank_name, ifsc_code, account_number, demate_number, country, state, city) VALUES (NULL,'{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}') """.format(user_id, hash_password, f_name, m_name, l_name, email, phone, pan_num, bank_name, ifsc_code,acc_num, demate, country, state, city))
            conn.commit()

            closing_balance = 0
            cur.execute(""" INSERT INTO `closing_balance`(id, user_id, closing_balance) VALUES (NULL,'{}','{}') """.format(user_id, closing_balance))
            conn.commit()
            return redirect(url_for('regi_mail'))
        else:
            a = ("<script type='text/javascript'>alert('This email address already taken, try different email address...');window.location.href='/registration'</script>")
            return (a)
    else:
        return redirect(url_for('base'))


@app.route('/regi_mail', methods=['POST','GET'])
def regi_mail():
    context = ssl.create_default_context()
    smtp = smtplib.SMTP_SSL('smtp.gmail.com',465, context=context)
    sender = "develofmyworld@gmail.com"
    receiver = info.regi_email
    subject = "Successfull opening a new account"
    body = """
Thank you! """+ str(info.regi_name).capitalize()+ """ 

    Successfully registration...
    Congratulations joining the Aapna stock ! the best option trading of Aapna stock.

    If you need any information about your account so contact our team,

    Help & Support So contact us develofmyworld@gmail.com

Terms of Service
Privacy Plicy

Aapna stock
"""
    smtp.login(sender,'jwzyzzafsotyaemu')
    em = EmailMessage()
    em['From'] = sender
    em['To'] = receiver
    em['Subject'] = subject
    em.set_content(body)
    smtp.sendmail(sender, receiver, em.as_string())
    smtp.quit()
    if smtp.quit:
        a = ("<script type='text/javascript'>alert('Successfully registation account...');window.location.href='/'</script>")
        return (a)
    else:
        a = ("<script type='text/javascript'>alert('Please try again...');window.location.href='/'</script>")
    return (a)




@app.route('/deposit', methods=['POST','GET'])
def deposit():
    conn = mysql.connector.connect(host="sql899.main-hosting.eu", user="u993197072_stock_market", password="Stock_market2023", database="u993197072_Stock_market")
    cur = conn.cursor()
    if request.method == 'POST':
        user_id = session['user_id'][0][1]
        amount = request.form.get('amount')
        card_number = request.form.get('card_number')
        deposit = "deposit"
        cur.execute(""" SELECT * FROM closing_balance WHERE user_id = '{}' """.format(user_id))
        res = cur.fetchall()
        closing_balance = res[0][2]
        if conn:
            cur.execute(""" INSERT INTO `deposit&withdraw` (id, user_id, amount,`deposit&withdraw`, `card_number&upi_id`) VALUES (NULL,'{}','{}','{}','{}') """.format(user_id, amount,deposit,card_number))
            conn.commit()

            total=(float(closing_balance)+float(amount))
            cur.execute(""" UPDATE `closing_balance` SET closing_balance = '{}' WHERE user_id = '{}' """.format(total,user_id))
            conn.commit()
            a = ("<script type='text/javascript'>alert('Successfull add deposit...');window.location.href='/fund'</script>")
            return (a)
        else:
            return redirect(url_for('base'))
    else:
        return redirect(url_for('base'))


@app.route('/withdraw', methods=['POST','GET'])
def withdraw():
    conn = mysql.connector.connect(host="sql899.main-hosting.eu", user="u993197072_stock_market", password="Stock_market2023", database="u993197072_Stock_market")
    cur = conn.cursor()
    if request.method == 'POST':
        user_id = session['user_id'][0][1]
        amount = request.form.get('amount')
        upi_id = request.form.get('upi_id')
        withdraw = "withdraw"
        if conn:
            cur.execute(""" SELECT * FROM closing_balance WHERE user_id = '{}' """.format(user_id))
            res = cur.fetchall()
            closing_balance = res[0][2]

            if float(closing_balance)>=float(amount):
                cur.execute(""" INSERT INTO `deposit&withdraw` (id, user_id, amount,`deposit&withdraw`, `card_number&upi_id`) VALUES (NULL,'{}','{}', '{}','{}') """.format(user_id, amount, withdraw, upi_id))
                conn.commit()
                if conn:
                    total = (float(closing_balance) - float(amount))
                    cur.execute(""" UPDATE `closing_balance` SET closing_balance = '{}' WHERE user_id = '{}' """.format(total, user_id))
                    conn.commit()
                    a = ("<script type='text/javascript'>alert('Successfull withdraw money...');window.location.href='/fund'</script>")
                    return (a)
                else:
                    pass
            else:
                a = ("<script type='text/javascript'>alert('Your balance is insufficient...');window.location.href='/fund'</script>")
                return (a)
        else:
            return redirect(url_for('base'))
    else:
        return redirect(url_for('base'))


@app.route('/buy_share', methods=['POST','GET'])
def buy_share():
    conn = mysql.connector.connect(host="sql899.main-hosting.eu", user="u993197072_stock_market", password="Stock_market2023", database="u993197072_Stock_market")
    cur = conn.cursor()
    if request.method == 'POST':
        user_id = session['user_id'][0][1]
        opening_share = 1000
        share_qty = request.form.get('qty')
        company_name = request.form.get('company_name')
        share_price = request.form.get('price')
        total_amount = request.form.get('total_amount')
        buy = "buy"
        sell = "sell"

        if conn:
            cur.execute(""" SELECT sum(qty) AS available FROM `buy&sell` WHERE `buy&sell` ='{}' && company_name='{}' """.format(buy,company_name))
            res1 = cur.fetchone()
            for x in res1:
                if x == None:
                    x = 0
                else:
                    x = x

            cur.execute(""" SELECT sum(qty) AS available FROM `buy&sell` WHERE `buy&sell` ='{}' && company_name='{}' """.format(sell,company_name))
            res = cur.fetchone()
            for y in res:
                if y == None:
                    y = 0
                else:
                    y = y

            available_share = opening_share - x + y

            if available_share >= int(share_qty):
                cur.execute(""" SELECT `closing_balance` FROM `closing_balance` WHERE user_id like '{}' """.format(user_id))
                closing_balance = cur.fetchone()
                for closing_balance in closing_balance:
                    closing_balance = closing_balance
                if float(closing_balance) >= float(total_amount):
                    cur.execute(""" INSERT INTO `buy&sell` (id, user_id, company_name, `buy&sell`, qty, price, total) VALUES (NULL,'{}','{}','{}','{}','{}','{}') """.format(user_id, company_name, buy, share_qty, share_price, total_amount))
                    conn.commit()

                    total = (float(closing_balance) - float(total_amount))
                    cur.execute(""" UPDATE `closing_balance` SET closing_balance = '{}' WHERE user_id = '{}' """.format(total, user_id))
                    conn.commit()
                    a = ("<script type='text/javascript'>alert('Successfull buy share...');window.location.href='/home'</script>")
                    return (a)
                else:
                    a = ("<script type='text/javascript'>alert('Your balance is insufficient please check your balance...');window.location.href='/home'</script>")
                    return (a)
            else:
                b = ("<script type='text/javascript'>alert('Not quantity avaible this share in this at time...');window.location.href='/home'</script>")
                return (b)
        else:
            return redirect(url_for('base'))
    else:
        return redirect(url_for('base'))


@app.route('/sell_share', methods=['POST','GET'])
def sell_share():
    conn = mysql.connector.connect(host="sql899.main-hosting.eu", user="u993197072_stock_market", password="Stock_market2023", database="u993197072_Stock_market")
    cur = conn.cursor()
    if 'user_id' in session:
        user_id = session['user_id'][0][1]
        cur.execute(""" SELECT `closing_balance` FROM `closing_balance` WHERE user_id like '{}' """.format(user_id))
        closing_balance = cur.fetchone()
        for closing_balance in closing_balance:
            closing_balance = closing_balance
        if request.method == 'POST':
            share_qty = request.form.get('qty')
            company_name = request.form.get('company_name')
            share_price = request.form.get('price')
            total_amount = request.form.get('total_amount')
            buy = "buy"
            sell = "sell"
            cur.execute(""" SELECT sum(qty) AS available FROM `buy&sell` WHERE `buy&sell` ='{}' && company_name='{}' && user_id = '{}' """.format(buy, company_name, user_id))
            res1 = cur.fetchone()
            for x in res1:
                if x == None:
                    x = 0
                else:
                    x = x
            cur.execute(""" SELECT sum(qty) AS available FROM `buy&sell` WHERE `buy&sell` ='{}' && company_name='{}'&& user_id = '{}' """.format(sell, company_name, user_id))
            res = cur.fetchone()
            for y in res:
                if y == None:
                    y = 0
                else:
                    y = y

            available_share = int(x - y)

            if conn:
                if int(available_share)  >= int(share_qty) :
                    cur.execute(""" INSERT INTO `buy&sell` (id, user_id, company_name, `buy&sell`, qty, price, total) VALUES (NULL,'{}','{}','{}','{}','{}','{}') """.format(user_id, company_name, sell, share_qty, share_price, total_amount))
                    conn.commit()

                    total = (float(closing_balance) + float(total_amount))
                    cur.execute(""" UPDATE `closing_balance` SET closing_balance = '{}' WHERE user_id = '{}' """.format(total, user_id))
                    conn.commit()
                    a = ("<script type='text/javascript'>alert('Successfull sell share...');window.location.href='/home'</script>")
                    return (a)
                else:
                    b = ("<script type='text/javascript'>alert('You to selled stock quantity more than available stock ...');window.location.href='/home'</script>")
                    return (b)
            else:
                pass
        else:
            return redirect(url_for('base'))
    else:
        return redirect(url_for('base'))


@app.route('/logout')
def logout():
    if 'user_id' in session:
        session.pop('user_id')
        return redirect(url_for('base'))
    else:
        return redirect(url_for('base'))


app.run(debug=True)