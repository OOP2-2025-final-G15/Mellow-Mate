def calculate_bmi(height, weight):
    """
    身長(cm)と体重(kg)からBMIを計算する関数
    """
    if not height or not weight:
        return None
    
    if height <= 0:
        return None

    # cm を m に変換
    height_m = height / 100
    
    # BMI計算式: 体重(kg) ÷ (身長(m) × 身長(m))
    bmi = weight / (height_m ** 2)
    
    # 小数点第2位で四捨五入して返す
    return round(bmi, 2)


# BMIの値から状態を判定する関数
def get_bmi_status(bmi):
    if bmi is None:
        return "-"
    
    if bmi < 18.5:
        return "低体重 (痩せ型)"
    elif 18.5 <= bmi < 25:
        return "普通体重"
    elif 25 <= bmi < 30:
        return "肥満 (1度)"
    elif 30 <= bmi < 35:
        return "肥満 (2度)"
    elif 35 <= bmi < 40:
        return "肥満 (3度)"
    else:
        return "肥満 (4度)"