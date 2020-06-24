# splite3をimportする
import sqlite3
# flaskをimportしてflaskを使えるようにする
from flask import Flask , render_template , request , redirect , session

from datetime import datetime

# appにFlaskを定義して使えるようにしています。Flask クラスのインスタンスを作って、 app という変数に代入しています。
app = Flask(__name__)

# Flask では標準で Flask.secret_key を設定すると、sessionを使うことができます。この時、Flask では session の内容を署名付きで Cookie に保存します。
app.secret_key = 'sunabakoza'

@app.route('/')
def index():
    return render_template('index.html')


# GET  /register => 登録画面を表示
# POST /register => 登録処理をする
@app.route('/register',methods=["GET", "POST"])
def register():
    #  登録ページを表示させる
    if request.method == "GET":
        if 'user_id' in session :
            return redirect ('/mypage')
        else:
            return render_template("register.html")
    # ここからPOSTの処理
    else:
        name = request.form.get("name")
        password = request.form.get("password")
        email = request.form.get("email")

        conn = sqlite3.connect('niseco.db')
        c = conn.cursor()
        c.execute("insert into user values(null,?,?,?,null,null,null,null,null,null)", (name,password,email))
        conn.commit()
        conn.close()
        return redirect('/login')


# GET  /login => ログイン画面を表示
# POST /login => ログイン処理をする
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if 'user_id' in session :
            return redirect("/mypage")
        else:
            return render_template("login.html")
    else:
        # ブラウザから送られてきたデータを受け取る
        email = request.form.get("email")
        password = request.form.get("password")

        # ブラウザから送られてきた name ,password を userテーブルに一致するレコードが
        # 存在するかを判定する。レコードが存在するとuser_idに整数が代入、存在しなければ nullが入る
        conn = sqlite3.connect('niseco.db')
        c = conn.cursor()
        c.execute("select id from user where email = ? and password = ?", (email, password) )
        user_id = c.fetchone()
        conn.close()

        # user_id が NULL(PythonではNone)じゃなければログイン成功
        if user_id is None:
            # ログイン失敗すると、ログイン画面に戻す
            return render_template("login.html")
        else:
            session['user_id'] = user_id[0]
            return redirect("/mypage")

# ログアウト機能
@app.route("/logout")
def logout():
    session.pop('user_id',None)
    # ログアウト後は最初のページにリダイレクトさせる
    return redirect("/")
   

# 会員用のページ
@app.route('/mypage')
def mypage():
    if 'user_id' in session :
        # クッキーからuser_idを取得
        user_id = session['user_id']
        conn = sqlite3.connect('niseco.db')
        c = conn.cursor()
        # # DBにアクセスしてログインしているユーザ名と投稿内容を取得する
        # クッキーから取得したuser_idを使用してuserテーブルのnameを取得
        c.execute("select 漢字氏名 from user where id = ?", (user_id,))
        # fetchoneはタプル型
        user_info = c.fetchone()
        
        c.close()
        return render_template('mypage.html' , user_info = user_info , user_id=user_id)
    else:
        return redirect("/login")


# 商品ページ作成
@app.route('/purchase_list', methods=["GET", "POST"])
def purchase_list():
    if 'user_id' in session :
        conn = sqlite3.connect('niseco.db')
        c = conn.cursor()
        c.execute("select id,商品名,税抜き価格 from 商品")
        comment_list = []
        for row in c.fetchall():
            comment_list.append({"id": row[0],"商品名": row[1], "税抜き価格": row[2]})

        c.close()
        return render_template('purchase_list.html' , comment_list = comment_list)
        # return render_template('purchase_list.html')
    else:
         return redirect("/login")


# 購入ページ作成
@app.route('/purchase/<int:id>', methods=["GET", "POST"])
def purchase_page(id):
    if 'user_id' in session :
        id = request.form.get("id")
        # print(id)
        conn = sqlite3.connect('niseco.db')
        c = conn.cursor()
        c.execute("select id,商品名,税抜き価格 from 商品 where id=?",(id,))
        comment_list = []
        for row in c.fetchall():
            comment_list.append({"id": row[0],"商品名": row[1], "税抜き価格": row[2]})
            
        c.close()
        return render_template('purchase.html' , comment_list = comment_list)

    else:
         return redirect("/login")


# 購入システム作成
@app.route('/purchase', methods=["GET", "POST"])
def purchase():
    if 'user_id' in session :
        time = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        user_id = session['user_id']
        print(user_id)
        商品id = request.form.get("商品id")
        print(商品id)
        商品名 = request.form.get("商品名")
        print(商品名)
        税抜き価格 = request.form.get("税抜き価格")
        print(税抜き価格)
        個数 = request.form.get("個数")
        print(個数)

        税抜き価格=int(税抜き価格)
        個数=int(個数)

        # 税込み価格の計算
        税込み価格 = 税抜き価格/10+税抜き価格
        print(税込み価格)
        # 合計金額の計算
        合計金額 = 税込み価格*個数

        
        conn = sqlite3.connect('niseco.db')
        c = conn.cursor()
        c.execute("insert into 購入履歴 values (null,?,?,?,?,?,?,?,?)",(user_id,time,商品id,商品名,個数,税抜き価格,税込み価格,合計金額,))
        conn.commit()
        conn.close()
        return redirect('/purchase_list')
        # return render_template('purchase.html')

    else:
         return redirect("/login")


# カートページ
@app.route('/cart', methods=["GET", "POST"])
def cart_page():
    if 'user_id' in session :
        id = request.form.get("id")
        # print(id)
        conn = sqlite3.connect('niseco.db')
        c = conn.cursor()
        c.execute("select 注文番号,購入者id,追加年月日,商品id,商品名,数量,税抜き価格,合計金額 from カート where 購入者id=? and del_flag = 0",(id,))
        comment_list = []
        for row in c.fetchall():
            comment_list.append({"注文番号": row[0],"購入者id": row[1], "追加年月日": row[2],"商品id": row[3],"商品名": row[4],"数量": row[5],"税抜き価格": row[6],"合計金額": row[6]})
            
        c.close()
        return render_template('cart.html' , comment_list = comment_list)

    else:
         return redirect("/login")


# カートに追加する動き
@app.route('/cart_in', methods=["GET", "POST"])
def cart_in():
    if 'user_id' in session :
        time = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        user_id = session['user_id']
        print(user_id)
        商品id = request.form.get("商品id")
        print(商品id)
        商品名 = request.form.get("商品名")
        print(商品名)
        税抜き価格 = request.form.get("税抜き価格")
        print(税抜き価格)
        個数 = request.form.get("個数")
        print(個数)

        税抜き価格=int(税抜き価格)
        個数=int(個数)
        # 税込み価格の計算
        税込み価格 = 税抜き価格/10+税抜き価格
        print(税込み価格)
        # 合計金額の計算
        合計金額 = 税込み価格*個数

        
        conn = sqlite3.connect('niseco.db')
        c = conn.cursor()
        c.execute("insert into カート values (null,?,?,?,?,?,?,?,?,0)",(user_id,time,商品id,商品名,個数,税抜き価格,税込み価格,合計金額,))
        conn.commit()
        conn.close()
        return redirect('/purchase_list')
        # return render_template('purchase.html')

    else:
         return redirect("/login")

# カート用の購入システム
@app.route('/cart_purchase', methods=["GET", "POST"])
def cart_purchase():
    if 'user_id' in session :
        time = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        user_id = session['user_id']
        print(user_id)
        商品id = request.form.get("商品id")
        print(商品id)
        商品名 = request.form.get("商品名")
        print(商品名)
        税抜き価格 = request.form.get("税抜き価格")
        print(税抜き価格)
        個数 = request.form.get("個数")
        print(個数)

        税抜き価格=int(税抜き価格)
        個数=int(個数)

        # 税込み価格の計算
        税込み価格 = 税抜き価格/10+税抜き価格
        print(税込み価格)
        # 合計金額の計算
        合計金額 = 税込み価格*個数

        
        conn = sqlite3.connect('niseco.db')
        c = conn.cursor()
        c.execute("insert into 購入履歴 values (null,?,?,?,?,?,?,?,?)",(user_id,time,商品id,商品名,個数,税抜き価格,税込み価格,合計金額,))
      

        注文番号 = request.form.get("注文番号")
        c.execute("update カート set del_flag = 1 where 注文番号=?", (注文番号,))
        conn.commit()
        conn.close()
        # return redirect('/purchase_list')
        # return redirect('/cart/<int:user_id>')
        return redirect('/cart')

    else:
         return redirect("/login")

# ここから管理人用

# GET  /login => ログイン画面を表示
# POST /login => ログイン処理をする
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        if 'admin_id' in session :
            return redirect("/admin_page")
        else:
            return render_template("admin_login.html")
    else:
        # ブラウザから送られてきたデータを受け取る
        name = request.form.get("name")
        password = request.form.get("password")

        # ブラウザから送られてきた name ,password を adminテーブルに一致するレコードが
        # 存在するかを判定する。レコードが存在するとadmin_idに整数が代入、存在しなければ nullが入る
        conn = sqlite3.connect('niseco.db')
        c = conn.cursor()
        c.execute("select id from admin where name = ? and password = ?", (name, password) )
        admin_id = c.fetchone()
        conn.close()

        # user_id が NULL(PythonではNone)じゃなければログイン成功
        if admin_id is None:
            # ログイン失敗すると、ログイン画面に戻す
            return render_template("admin_login.html")
        else:
            session['admin_id'] = admin_id[0]
            return redirect("/admin_page")

# ログアウト機能
@app.route("/admin_logout")
def admin_logout():
    session.pop('admin_id',None)
    # ログアウト後は最初のページにリダイレクトさせる
    return redirect("/")
   

# 会員用のページ
@app.route('/admin_page')
def admin_page():
    if 'admin_id' in session :
        # クッキーからadmin_idを取得
        admin_id = session['admin_id']
        # print(admin_id)
        conn = sqlite3.connect('niseco.db')
        c = conn.cursor()
        # # DBにアクセスしてログインしているユーザ名と投稿内容を取得する
        # クッキーから取得したadmin_idを使用してadminテーブルのnameを取得
        c.execute("select name from admin where id = ?", (admin_id,))
        # fetchoneはタプル型
        admin_info = c.fetchone()
        c.execute("select id,商品名,税抜き価格,税込み価格,登録日時 from 商品")
        comment_list = []
        for row in c.fetchall():
            comment_list.append({"id": row[0],"商品名": row[1], "税抜き価格": row[2], "税込み価格": row[3], "登録日時": row[4]})
        c.close()
        return render_template('admin_page.html' , admin_info = admin_info , comment_list = comment_list)
    else:
        return redirect("/admin_login")



# 商品登録
@app.route('/commodity_add' , methods=["POST"])
def commodity_add():
    # admin_id = session['admin_id']
    time = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    print(time)
    # フォームから入力されたアイテム名の取得
    商品名 = request.form.get("商品名")
    print(商品名)
    # 商品名 = str(商品名)
    税抜き価格 = request.form.get("税抜き価格")
    print(税抜き価格)
    税抜き価格=int(税抜き価格)
    # 税込み価格の計算
    税込み価格 = 税抜き価格/10+税抜き価格
    print(税込み価格)

    conn = sqlite3.connect('niseco.db')
    c = conn.cursor()
    # DBにデータを追加する
    c.execute("insert into 商品 values (null,?,?,?,?)", (商品名,税抜き価格,税込み価格,time,))
    # c.execute("insert into 商品 values (null,null,null,null,null)")
    
    conn.commit()
    conn.close()
    return redirect('/admin_page')


# 購入履歴の確認
@app.route('/purchase_history' , methods=["GET"])
def purchase_history():
    if 'admin_id' in session :
        conn = sqlite3.connect('niseco.db')
        c = conn.cursor()
        c.execute("select 注文番号,購入者id,購入年月日,商品id,商品名,数量,税抜き価格,税込み価格,合計金額 from 購入履歴")
        comment_list = []
        for row in c.fetchall():
            comment_list.append({"注文番号": row[0], "購入者id": row[1], "購入年月日": row[2], "商品id": row[3], "商品名": row[4], "数量": row[5], "税抜き価格": row[6], "税込み価格": row[7], "合計金額": row[8]})

        c.close()
        return render_template('purchase_history.html'  , comment_list = comment_list)
    else:
        return redirect("/admin_login")


# 登録されているユーザーの確認
@app.route('/registered_users' , methods=["GET"])
def registered_users():
    if 'admin_id' in session :
        conn = sqlite3.connect('niseco.db')
        c = conn.cursor()
        c.execute("select * from user")
        comment_list = []
        for row in c.fetchall():
            comment_list.append({"user_id": row[0], "漢字氏名": row[1], "カナ氏名": row[2], "email": row[3], "password": row[4]})
        
        c.close()
        return render_template('registered_users.html'  , comment_list = comment_list)
    else:
        return redirect("/admin_login")




@app.errorhandler(403)
def mistake403(code):
    return 'There is a mistake in your url!'


@app.errorhandler(404)
def notfound404(code):
    return "404だよ！！見つからないよ！！！"


# __name__ というのは、自動的に定義される変数で、現在のファイル(モジュール)名が入ります。 ファイルをスクリプトとして直接実行した場合、 __name__ は __main__ になります。
if __name__ == "__main__":
    # Flask が持っている開発用サーバーを、実行します。
    app.run()