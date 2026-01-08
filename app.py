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
from peewee import *
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
import datetime

app = Flask(__name__)

# --- 設定周り ---
app.config['SECRET_KEY'] = 'your_secret_key'

# データベースの設定 (Peewee)
db = SqliteDatabase('health.db')

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

# --- データベース接続ハンドラ ---
# リクエストが来るたびにDBにつなぎ、終わったら切断する設定
@app.before_request
def before_request():
    db.connect()

@app.teardown_request
def _db_close(exc):
    if not db.is_closed():
        db.close()

# --- モデル定義 (Peewee) ---

# 基本モデル（DB設定を共通化するためのクラス）
class BaseModel(Model):
    class Meta:
        database = db

# 1. ユーザー情報
class User(UserMixin, BaseModel):
    userName = CharField(unique=True) # 文字列
    password = CharField()
    
    # プロフィール
    age = IntegerField()           # 整数
    gender = IntegerField()        # 1:男性, 2:女性, 0:その他
    height = FloatField()          # 小数
    weight = FloatField()
    
    # 目標設定(任意)
    targetWeight = FloatField(null=True)
    targetCalories = IntegerField(null=True)

    # パスワード関連メソッド
    # 新規登録のとき使う
    def set_password(self, password):
        # passwordをハッシュ化して保存
        # password:ユーザーが入力した生のパスワード
        # 生成されたハッシュを self.password に保存
        self.password = generate_password_hash(password)

    # ログインする時に使う
    def check_password(self, password):
        # 入力されたパスワードが保存されているハッシュと一致するか確認
        return check_password_hash(self.password, password)

# 2. 日々の記録
class DailyRecord(BaseModel):
    # ForeignKeyField(外部キー)でUserと紐付け (backrefで user.daily_records とアクセス可能に)
    user = ForeignKeyField(User, backref='daily_records')
    # date = DateField(default=datetime.date.today)は日付を自動入力する
    date = DateField(default=datetime.date.today)
    
    # 変動データ
    weight = FloatField(null=True) # 体重
    intakeCalories = IntegerField(default=0) # 摂取カロリー
    burnedCalories = IntegerField(default=0) # 消費カロリー
    waterIntake = FloatField(default=0.0) # 水分量
    stepCount = IntegerField(default=0) # 歩数

# 3. 食べ物
class Food(BaseModel):
    name = CharField()
    calories = IntegerField()

# 4. 食事ログ（いつ・何を・どの食事）
class FoodLog(BaseModel):
    user = ForeignKeyField(User, backref='food_logs')
    record_date = DateField(default=datetime.date.today)
    meal_time = CharField()  # "朝", "昼", "夜"
    food = ForeignKeyField(Food)

# --- DB初期化 ---
# テーブルがなければ作成する
with db:
    db.create_tables([User, DailyRecord, Food, FoodLog])


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

# 食事とカロリー登録
@app.route("/tracking/food", methods=["GET", "POST"])
@login_required
def input_food():
    if request.method == "POST":
        food_name = request.form.get("food_name")
        calories = int(request.form.get("calories"))

        # Foodテーブルに登録
        Food.create(
            name=food_name,
            calories=calories
        )

        return redirect(url_for("calories"))

    return render_template("tracking/input_food.html")

# 食事記録
@app.route("/tracking/calories", methods=["GET", "POST"])
@login_required
def calories():
    if request.method == "POST":
        food_id = int(request.form.get("food_id"))
        meal_time = request.form.get("meal_time")
        record_date = request.form.get("record_date")
        # 食事ログを保存
        FoodLog.create(
            user=current_user,
            food=Food.get_by_id(food_id),
            meal_time=meal_time,
            record_date=record_date
        )
        # 登録後は同じページに戻る
        return redirect(url_for("calories"))

    foods = Food.select()
    today = datetime.date.today()


# ★ 仮表示用にその日の食事ログを取得
    logs = (
        FoodLog
        .select(FoodLog, Food)
        .join(Food)
        .where(
            (FoodLog.user == current_user) &
            (FoodLog.record_date == today)
        )
    )

    # ★ 合計カロリーを計算
    total_calories = sum(log.food.calories for log in logs)
    return render_template(
        "tracking/calories.html",
        foods=foods,
        today=today,
        logs=logs,
        total_calories=total_calories
    )
    
# 体重記録
@app.route("/tracking/weight", methods=["GET", "POST"])
@login_required
def weight():
    if request.method == "POST":
        record_date = request.form.get("record_date")
        weight_value = float(request.form.get("weight"))

        record, created = DailyRecord.get_or_create(
            user=current_user,
            date=record_date
        )

        record.weight = weight_value
        record.save()

        return redirect(url_for("dashboard"))

    today = datetime.date.today()
    return render_template("tracking/weight.html", today=today)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)