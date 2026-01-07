# アプリ起動用メインファイル

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# ホームページのルート
@app.route('/')
def index():
    return render_template('index.html')

# ログインのルート
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # ログイン処理
        username = request.form['userName']
        password = request.form['password']
        # ここで認証ロジックを追加
        # 現在はしていない
        return redirect(url_for('dashboard'))
    return render_template('auth/login.html')

# プロフィール設定のルート
@app.route('/profile_setup', methods=['GET', 'POST'])
def profile_setup():
    if request.method == 'POST':
        # プロフィール設定処理
        username = request.form['userName']
        age = request.form['age']
        height = request.form['height']
        weight = request.form['weight']
        gender = request.form['gender']
        password = request.form['password']
        # ここでユーザーデータ保存ロジックを追加
        # 現在はしていない
        return redirect(url_for('goals'))
    return render_template('auth/profile_setup.html')

# 現状使っていない？？
@app.route('/register')
def register():
    return render_template('auth/register.html')

# 目標設定画面のルート
@app.route('/goals')
def goals():
    return render_template('main/goals.html')

# ホーム画面のルート
@app.route('/dashboard')
def dashboard():
    return render_template('main/dashboard.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
