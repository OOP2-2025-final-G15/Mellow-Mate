# アプリ起動用メインファイル

from flask import Flask, render_template


app = Flask(__name__)

# ホームページのルート
@app.route('/')
def index():
    return render_template(
        'user/settings.html',
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
