import csv
import random
import string
from datetime import datetime, timedelta

# הגדרת פרמטרים לייצור הדאטה
NUM_POSTS = 4000
TARGET_HASHTAGS = ["#CocaColaMY", "#FIFAWorldCup", "#TrophyTour", "#AllTheFeels"]

# 1. בריכת תוכן לגיטימי של משפיענים ומעריצים באינסטגרם
legitimate_contents = [
    "Saksikan sendiri Trofi Piala Dunia FIFA! Unbelievable experience being this close to football history 🏆⚽ Thank you {} for making this happen! ❤️",
    "Currently at the venue and the energy is absolutely insane! Who are you rooting for in 2026? 🇨🇦🇲🇽🇺🇸 #FIFAWorldCup",
    "Can’t believe in a few hours I'll be seeing the World Cup Trophy live. EXCITINGGG! Drop a comment if you are coming down to Sunway Pyramid! 👇",
    "Celebrating the beautiful game with cold drinks, good music, and the best crowd. Swipe left to see more photos! 👉📸",
    "Honoured to welcome the trophy. What an iconic day it was on the tour with the team!",
    "Football is not just a sport, it's a lifestyle. Living for these moments! ✨🥤 #AllTheFeels"
]

# 2. בריכת תוכן חטוף (Hard Negatives - בוטים, קריפטו, הימורים, ספאם של עוקבים)
hijacked_contents = [
    "🔥 LINK IN BIO FOR FAST CASH! Earn $200-$600 daily using just your phone. No experience needed! 🤑💸",
    "Want 10K REAL Instagram followers and likes instantly? 🚀 Cheap prices, active accounts, fast delivery! Check the link in our bio 👇",
    "Guaranteed 95% win rate on all football matches tonight! Don't lose money, join our VIP Telegram channel via bio link! 🎰⚽",
    "MASSIVE NFT GIVEAWAY! 🎁 We are dropping 100 rare items. To enter: Like this post, tag 3 friends, and click the bio link!",
    "Best online dating and webcam community 🔞 Chat with lonely girls near you right now. Link in bio!",
    "Crypto market is pumping! Best time to invest in our new token before it goes 100x. Don't miss out! 📈💰"
]

# שמות משתמשים טיפוסיים לאינסטגרם
good_users = ["princess_burland", "mich8lee", "travel_blogger_my", "soccer_vibes", "malaysia_foodie", "kicks_crew", "urban_explorer"]
bot_users = ["crypto_queen_99", "casino_king_bot", "gain_followers_fast", "sexy_babe_insta", "nft_whale_alert", "spam_deals_2026"]

# פונקציה לייצור מזהה פוסט ייחודי של אינסטגרם (Shortcode - כמו P/C_x1y2z3)
def generate_instagram_shortcode():
    chars = string.ascii_letters + string.digits + "_-"
    return "".join(random.choice(chars) for _ in range(11))

posts_data = []
start_date = datetime(2026, 1, 1)

# יחס ויראלי: 55% לגיטימי (משפיענים/קהל אמיתי), 45% חטוף (ספאם/בוטים)
for i in range(NUM_POSTS):
    shortcode = generate_instagram_shortcode()
    post_id = random.randint(3700000000000000000, 3900000000000000000)
    
    # הגרלת תאריכים לאורך ינואר-פברואר 2026
    random_days = random.randint(0, 50)
    random_hours = random.randint(0, 23)
    random_minutes = random.randint(0, 59)
    post_time = start_date + timedelta(days=random_days, hours=random_hours, minutes=random_minutes)
    timestamp = post_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    
    is_legit = random.random() > 0.45  # 55% סיכוי לפוסט תקין
    
    if is_legit:
        target_hashtag = "seed"
        username = random.choice(good_users) if random.random() > 0.3 else f"user_{random.randint(1000, 9999)}"
        base_content = random.choice(legitimate_contents).format(TARGET_HASHTAGS[0])
        hashtags_str = ", ".join(random.sample(TARGET_HASHTAGS, k=random.randint(2, 4)))
        content = f"{base_content}\n.\n.\n{hashtags_str}"
        
        # אינסטגרם אורגני: מעורבות גבוהה יחסית
        num_likes = random.randint(150, 35000)
        num_comments = random.randint(10, 1200)
        num_shares = random.randint(5, 400)
        score = 1  # לגיטימי
    else:
        target_hashtag = "hijacked"
        username = random.choice(bot_users) + str(random.randint(10, 99))
        base_content = random.choice(hijacked_contents)
        # בוטים דוחפים את כל ההאשטגים הפופולריים יחד כדי לעלות בחיפושים
        hashtags_str = ", ".join(TARGET_HASHTAGS)
        content = f"{base_content}\n\n{hashtags_str}"
        
        # פרופילי ספאם: הרבה פוסטים, כמעט אפס מעורבות אמיתית
        num_likes = random.randint(0, 25)
        num_comments = random.randint(0, 3)
        num_shares = 0
        score = 0  # חטוף

    url = f"https://www.instagram.com/p/{shortcode}/"
    
    posts_data.append([
        target_hashtag, post_id, username, hashtags_str, timestamp, content, num_likes, num_comments, num_shares, url, score
    ])

# כתיבה לקובץ CSV במבנה מותאם לאינסטגרם
csv_columns = ["target_hashtag", "post_id", "username", "hashtags", "timestamp", "content", "num_likes", "num_comments", "num_shares", "url", "score"]

with open("instagram_campaign_data.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(csv_columns)
    writer.writerows(posts_data)

print(f"Successfully generated instagram_campaign_data.csv with {NUM_POSTS} records!")