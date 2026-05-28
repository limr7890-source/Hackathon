import pandas as pd

def get_mock_model_results():
    """
    פונקציה שמחזירה בדיוק את סוג המידע והמבנה שהמודל של החברים הולך לייצר.
    היא כוללת את ההאשטאג, תוכן הפוסט, מדדי המעורבות (לייקים ותגובות) והסיווג (0 או 1).
    """
    data = {
        "Target_Hashtag": [
            "#JustDoIt", "#JustDoIt", "#WorldCup", "#JustDoIt", "#WorldCup",
            "#JustDoIt", "#WorldCup", "#WorldCup", "#JustDoIt", "#WorldCup"
        ],
        "Post_Text": [
            "Just finished my morning run! Loving the new shoes, perfect fit.",
            "Buy fake luxury watches for 90% off right now! Click here",
            "What a goal! The stadium is absolutely electric tonight!! ⚽",
            "Look at my cute cat sleeping on the couch today, so adorable.",
            "Crypto flash sale! Double your coins in 24 hours link in bio 🚀",
            "No excuses. Pushing limits at the gym today. #Motivation",
            "Amazing match, team played heart out, but we lost in penalties.",
            "Earn 5000$ a day working from home, guaranteed payout, DM me!",
            "New workout gear arrived, time to test it on the track!",
            "Unrelated political comment that has nothing to do with football."
        ],
        "Likes": [1250, 3200, 8500, 45, 910, 2100, 6400, 1500, 890, 310],
        "Comments": [45, 810, 420, 2, 115, 88, 312, 430, 19, 75],
        "Model_Label": [1, 0, 1, 0, 0, 1, 1, 0, 1, 0]  # 1 = תואם, 0 = לא קשור/ספאם
    }
    
    # הופך את המילון לטבלת דאטה-פריים רשמית של Pandas
    df = pd.DataFrame(data)
    return df

# אם מריצים את הקובץ הזה ישירות, הוא פשוט ידפיס את הטבלה למסך לראות שהכל תקין
if __name__ == "__main__":
    df_example = get_mock_model_results()
    print("--- הנה דוגמה מדויקת לנתונים שאת הולכת לקבל מהמודלים: ---")
    print(df_example)