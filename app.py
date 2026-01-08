# # アプリ起動用メインファイル

# from flask import Flask, render_template


# app = Flask(__name__)

# # ホームページのルート
# @app.route('/')
# def index():
#     return render_template(
#         'index.html',
#     )

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8080, debug=True)


import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager,login_user, login_required, logout_user, current_user
import datetime

# db_manager.py からクラスや変数を読み込み
from db_manager import db, User, DailyRecord, initialize_database

app = Flask(__name__)

# 設定
app.config['SECRET_KEY'] = 'your_secret_key'

# データベース接続ハンドラ
# リクエストが来るたびにDBにつなぎ、終わったら切断する設定
@app.before_request
def before_request():
    db.connect()

@app.teardown_request
def _db_close(exc):
    if not db.is_closed():
        db.close()

# アプリ起動時の初期化
# 最初に1回だけ実行してテーブルを作る
initialize_database()


# --- ログイン管理の設定 ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.get(User.id == int(user_id))
    except User.DoesNotExist:
        return None

# --- DB初期化 ---
# テーブルがなければ作成する
# with db:
#     db.create_tables([User, DailyRecord])

# --- ルーティング ---

@app.route('/')
def index():
    return render_template('index.html')

# ① 新規登録
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        userName = request.form['userName']
        password = request.form['password']
        
        try:
            age = int(request.form['age'])
            gender = int(request.form['gender'])
            height = float(request.form['height'])
            weight = float(request.form['weight'])
        except ValueError:
            flash("数値の入力形式が正しくありません")
            return redirect(url_for('register'))

        # 重複チェック (Peewee流: get_or_none)
        if User.get_or_none(User.userName == userName):
            flash('そのユーザー名は既に使用されています。')
            return redirect(url_for('register'))

        # ユーザー作成
        # Peeweeではインスタンス化して .save() するか、.create() を使う
        new_user = User(
            userName=userName, 
            age=age, 
            gender=gender, 
            height=height, 
            weight=weight
        )
        new_user.set_password(password)
        new_user.save() # 保存！
        
        # 今日の記録を作成
        DailyRecord.create(
            user=new_user, 
            weight=weight, 
            date=datetime.date.today()
        )

        flash('登録完了！ログインしてください。')
        return redirect(url_for('login'))

    return render_template('auth/profile_setup.html')

# ④ ログイン
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userName = request.form['userName']
        password = request.form['password']
        
        # ユーザー検索
        user = User.get_or_none(User.userName == userName)
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('ユーザー名またはパスワードが違います。')
    return render_template('auth/login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('main/dashboard.html', user=current_user)

# ユーザー設定
@app.route('/user/settings', methods=['GET', 'POST'])
@login_required
def update_settings():
    if request.method == 'POST':
        # データの更新
        current_user.userName = request.form['userName']
        current_user.height = float(request.form['height'])
        current_user.gender = int(request.form['gender']) # HTML側で修正が必要かも(数値送信ならOK)
        current_user.age = int(request.form['age'])
        
        current_user.save() # Peeweeでの更新保存
        
        flash('設定を更新しました。')
        return redirect(url_for('update_settings'))

    return render_template('user/settings.html', current_user=current_user)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)