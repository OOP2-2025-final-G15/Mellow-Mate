def calculate_burned_calories(user, current_weight, steps):
    """
    基礎代謝 + 歩数分の消費カロリーを計算する関数
    """
    
    # 1. 基礎代謝 (BMR) の計算
    # ハリス・ベネディクト方程式 (日本人版に近い計算式)
    # 男性: 66 + 13.7×体重 + 5.0×身長 - 6.8×年齢
    # 女性: 665 + 9.6×体重 + 1.8×身長 - 4.7×年齢
    
    age = user.age
    height = user.height
    weight = current_weight  # 今日の体重（なければ登録時の体重）
    
    if user.gender == 1: # 男性
        bmr = 66 + (13.7 * weight) + (5.0 * height) - (6.8 * age)
    else: # 女性 (またはその他)
        bmr = 665 + (9.6 * weight) + (1.8 * height) - (4.7 * age)

    # 2. 歩数による消費カロリー
    # ざっくり 1歩 = 0.04kcal と仮定
    step_calories = steps * 0.04
    
    # 合計を整数にして返す
    total_burned = int(bmr + step_calories)
    
    return total_burned