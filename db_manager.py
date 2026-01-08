from peewee import *
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

# データベース本体の設定
# ここでデータベースファイル名を指定
db = SqliteDatabase('health.db')

# モデル（設計図）の定義

# 基本モデル（共通設定）
class BaseModel(Model):
    class Meta:
        database = db

# ユーザー情報テーブル
class User(UserMixin, BaseModel):
    userName = CharField(unique=True)
    password = CharField()
    
    # プロフィール
    age = IntegerField()
    gender = IntegerField(choices=((1, '男性'), (2, '女性'), (0, 'その他'))) 
    height = FloatField()
    weight = FloatField()
    
    # 目標設定()
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

# 日々の記録テーブル
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

# --- 3. 便利関数（初期化用） ---
def initialize_database():
# テーブルが存在しない場合に作成する関数
    db.connect()
    db.create_tables([User, DailyRecord], safe=True)
    db.close()