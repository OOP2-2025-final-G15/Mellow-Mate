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
from utils import calculate_burned_calories

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

# @app.route('/dashboard')
# @login_required
# def dashboard():
#     today = datetime.date.today()
#     logs = (FoodLog.select(FoodLog, Food)
#             .join(Food)
#             .where((FoodLog.user == current_user) & (FoodLog.record_date == today)))
    
#     total_calories = sum(log.food.calories for log in logs)
    
#     # 体重・歩数・水分の取得
#     # 今日のDailyRecordを取得
#     daily_record = DailyRecord.get_or_none(
#         (DailyRecord.user == current_user) & (DailyRecord.date == today)
#     )

#     # レコードがあればその値を、なければ0やユーザーのデフォルト値を使う
#     current_weight = daily_record.weight if daily_record and daily_record.weight else current_user.weight
#     stepCount = daily_record.stepCount if daily_record else 0
#     waterIntake = daily_record.waterIntake if daily_record else 0

#     # 消費カロリー計算
#     burned_calories = calculate_burned_calories(current_user, current_weight, stepCount)

#     return render_template('main/dashboard.html', 
#                            user=current_user,
#                            total_calories=total_calories, # 計算したカロリー
#                            current_weight=current_weight, # 今日の体重
#                            steps=stepCount,                   # 今日の歩数
#                            water=waterIntake,                  # 今日の水分摂取量   
#                            burned_calories=burned_calories)     # 今日の消費カロリー              


# ③ 目標設定・確認画面
@app.route('/goals', methods=['GET', 'POST'])
@login_required
def goals():
    if request.method == 'POST':
        # フォームから取得
        targetWeight = request.form.get("targetWeight")
        targetCalories = request.form.get("targetCalories")

        # 型変換と保存
        if targetWeight:
            current_user.targetWeight = float(targetWeight)
        if targetCalories:
            current_user.targetCalories = int(targetCalories)

        current_user.save()  # Peewee 保存

        flash("目標を更新しました。")
        return redirect(url_for("goals"))

    # 表示するためにテンプレに渡す
    return render_template(
        "main/goals.html",
        current_user=current_user
    )

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

# --- 追加：トラッキング機能のルート ---
from db_manager import Food, FoodLog, initialize_extended_database

# 起動時の初期化を新しい関数に差し替え
initialize_extended_database()

@app.route("/tracking/food", methods=["GET", "POST"])
@login_required
def input_food():
    if request.method == "POST":
        food_name = request.form.get("food_name")
        calories = int(request.form.get("calories"))
        Food.create(name=food_name, calories=calories)
        return redirect(url_for("calories"))
    return render_template("tracking/input_food.html")

@app.route("/tracking/calories", methods=["GET", "POST"])
@login_required
def calories():
    date_str = request.args.get("date")
    if date_str:
        try:
            # 文字列を日付データに変換
            today = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            today = datetime.date.today()
    else:
        today = datetime.date.today()
    if request.method == "POST":
        food_id_val = request.form.get("food_id")
        if not food_id_val:
            flash("食べ物が選択されていません。まずは「＋食べ物を追加」から登録してください。")
            return redirect(url_for("calories"))
        food_id = int(food_id_val)
        meal_time = request.form.get("meal_time")
        record_date = request.form.get("record_date")
        
        FoodLog.create(
            user=current_user,
            food=Food.get_by_id(food_id),
            meal_time=meal_time,
            record_date=record_date
        )
        # 登録した日付のページを表示するようにリダイレクト先を変更
        return redirect(url_for("calories",date=record_date))
    # GET時の表示用データ作成
    foods = Food.select()
    # today = datetime.date.today()
    logs = (FoodLog.select(FoodLog, Food).join(Food)
            .where((FoodLog.user == current_user) & (FoodLog.record_date == today)))
    
    total_calories = sum(log.food.calories for log in logs)
    return render_template("tracking/calories.html", foods=foods, today=today, logs=logs, total_calories=total_calories)

@app.route("/tracking/weight", methods=["GET", "POST"])
@login_required
def weight():
    if request.method == "POST":
        record_date = request.form.get("record_date")
        weight_value = float(request.form.get("weight"))
        record, created = DailyRecord.get_or_create(user=current_user, date=record_date)
        record.weight = weight_value
        record.save()
        return redirect(url_for("dashboard"))

    today = datetime.date.today()
    return render_template("tracking/weight.html", today=today)

@app.route("/tracking/waterIntake", methods=["GET", "POST"])
@login_required
def waterIntake():
    if request.method == "POST":
        record_date = request.form.get("record_date")
        amount = float(request.form.get("amount"))
        record, created = DailyRecord.get_or_create(user=current_user, date=record_date)
        record.waterIntake = amount
        record.save()
        return redirect(url_for("dashboard"))

    today = datetime.date.today()
    return render_template("tracking/waterIntake.html", today=today)

@app.route("/tracking/stepCount", methods=["GET", "POST"])
@login_required
def stepCount():
    if request.method == "POST":
        record_date = request.form.get("record_date")
        steps = int(request.form.get("steps"))
        record, created = DailyRecord.get_or_create(user=current_user, date=record_date)
        record.stepCount = steps
        record.save()
        return redirect(url_for("dashboard"))

    today = datetime.date.today()
    return render_template("tracking/stepCount.html", today=today)

# --- グラフの1ヶ月表示対応のためのアップデート (既存のdashboardを上書き) ---
import calendar

@app.route('/dashboard')
@login_required
def dashboard():
    today = datetime.date.today()
    
    # 1. 表示する月の決定 (プルダウンで選択された月、または今月)
    year = int(request.args.get('year', today.year))
    month = int(request.args.get('month', today.month))
    
    # 2. その月の日数を取得
    _, last_day = calendar.monthrange(year, month)
    
    # 3. 1ヶ月分のデータを0で初期化して用意
    intake_list = [0] * last_day
    burned_list = [0] * last_day
    
    # 4. 1ヶ月分の食事記録 (FoodLog) を取得
    month_logs = (FoodLog.select(FoodLog, Food).join(Food)
                 .where((FoodLog.user == current_user) & 
                        (FoodLog.record_date >= datetime.date(year, month, 1)) &
                        (FoodLog.record_date <= datetime.date(year, month, last_day))))
    
    for log in month_logs:
        day_index = log.record_date.day - 1
        intake_list[day_index] += log.food.calories

    # 5. 1ヶ月分の活動記録 (DailyRecord) を取得
    month_records = (DailyRecord.select()
                    .where((DailyRecord.user == current_user) &
                           (DailyRecord.date >= datetime.date(year, month, 1)) &
                           (DailyRecord.date <= datetime.date(year, month, last_day))))
    
    for rec in month_records:
        day_index = rec.date.day - 1
        # 消費カロリーを計算してリストに入れる
        weight_at_time = rec.weight if rec.weight else current_user.weight
        steps_at_time = rec.stepCount if rec.stepCount else 0
        burned = calculate_burned_calories(current_user, weight_at_time, steps_at_time)
        burned_list[day_index] = burned

    # 今日の数値（画面下部の表示用）
    daily_record = DailyRecord.get_or_none((DailyRecord.user == current_user) & (DailyRecord.date == today))
    current_weight = daily_record.weight if daily_record and daily_record.weight else current_user.weight
    
    return render_template('main/dashboard.html', 
                           user=current_user,
                           intake_list=intake_list,   # ★グラフ用の1ヶ月リスト
                           burned_list=burned_list,   # ★グラフ用の1ヶ月リスト
                           total_calories=intake_list[today.day-1], # 今日の分
                           current_weight=current_weight,
                           steps=daily_record.stepCount if daily_record else 0,
                           water=daily_record.waterIntake if daily_record else 0,
                           burned_calories=burned_list[today.day-1]) # 今日の分

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)