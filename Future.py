import yfinance as yf
import pandas as pd
import time

# تعريف بيانات تسجيل الدخول الخاصة بك
username = "KhaLedDzTrader"
password = "DzTraderK"

# إعداد مدة الصفقة
durations = {
    "1M": "1min",
    "5M": "5min",
    "1D": "1d",
}

# بيانات الأزواج (OTC)
pairs = {
    1: "BRL/USD_OTC",
    2: "USD/BDT_OTC",
    3: "USD/PKR_OTC",
    4: "USD/INR_OTC",
    5: "USD/MXN_OTC",
    6: "USD/DZD_OTC",
    7: "USD/CAD_OTC",
    8: "NZD/CAD_OTC",
    9: "EUR/AUD_OTC"
}

# تحليل البيانات التاريخية بناءً على اليوم (من 1 يوم إلى 30 يوم)
def get_historical_data(pair, duration):
    # استرجاع البيانات باستخدام yfinance
    ticker = yf.Ticker(pair)
    data = ticker.history(period=duration)
    return data

# تحديد المدة وتحليل البيانات
def analyze_data(pair_choice, duration_choice):
    pair = pairs[pair_choice]
    duration = durations[duration_choice]
    
    # الحصول على البيانات التاريخية
    print(f"Analyzing data for {pair} with duration {duration}...")
    historical_data = get_historical_data(pair, duration)
    
    # تحليل البيانات هنا - يمكن إضافة استراتيجيات التحليل مثل Moving Averages أو Indicators
    print(historical_data.tail())  # عرض آخر 5 سجلات للتحليل

# اختيار الاتجاه (CALL أو PUT)
def choose_direction():
    direction = input("Choose direction (CALL/PUT): ").upper()
    if direction not in ['CALL', 'PUT']:
        print("Invalid input. Please choose CALL or PUT.")
        return choose_direction()
    return direction

# اختيار الزوج
def choose_pair():
    print("Choose a pair from the following options:")
    for key, value in pairs.items():
        print(f"{key}. {value}")
    pair_choice = int(input("Enter the number of the pair: "))
    if pair_choice not in pairs:
        print("Invalid choice. Please choose a valid pair.")
        return choose_pair()
    return pair_choice

# تحديد مدة الصفقة
def choose_duration():
    print("Choose the duration of the trade:")
    print("1. 1 Minute (1M)")
    print("2. 5 Minutes (5M)")
    duration_choice = int(input("Enter the number of the duration: "))
    if duration_choice not in [1, 2]:
        print("Invalid choice. Please choose a valid duration.")
        return choose_duration()
    return "1M" if duration_choice == 1 else "5M"

# استخراج البيانات وتحليلها
def run_analysis():
    print("Welcome to Quotex Analysis Script!")

    # اختيار الأزواج والمدة
    pair_choice = choose_pair()
    duration_choice = choose_duration()
    
    # تحليل البيانات
    analyze_data(pair_choice, duration_choice)
    
    # اختيار الاتجاه
    direction = choose_direction()
    
    # هنا، يمكننا إضافة استراتيجية تحليل البيانات التاريخية لتحديد هل ندخل في صفقة CALL أو PUT

    print(f"Ready to place a {direction} trade on {pairs[pair_choice]} for duration {duration_choice}...")

# استدعاء الدالة الرئيسية
if __name__ == "__main__":
    run_analysis()
