import csv
import random
from datetime import datetime, timedelta

# הגדרות ה-Dataset
TOTAL_POSTS = 4000
SPAM_RATIO = 0.22 
OUTPUT_FILE = "coca_cola_trophy_tour_sophisticated.csv"

# משתמשים לגיטימיים
USERNAMES_LEGIT = [
    "football_fever26", "worldcup_tracker", "coca_cola_fan_zone", "mexico_2026_vibes",
    "juan_soccer_la", "soccer_moments_hd", "princess_burland", "mich8lee",
    "stadium_chaser", "buenosaires_goals", "malaysia_sports_hub", "canada_kicks",
    "gilberto_fan_page", "pitch_side_story", "road_to_2026", "toronto_fc_guy"
]

# משתמשים "רוכבי טרנדים" (Hijackers - פרופילים שנראים אמיתיים אבל מנצלים את הטרנד לקידום עצמי)
USERNAMES_HIJACK = [
    "fitness_lifestyle_26", "crypto_news_daily", "deals_finder_global", "travel_bug_vlogs",
    "hype_sneakers_uk", "streetwear_daily", "makeup_by_sophia", "tech_trends_now",
    "foodie_explorer", "meme_lord_central"
]

# תבניות תוכן (לגיטימי)
legit_templates = [
    "I still can't believe the original FIFA World Cup trophy is actually here! 🏆 Matches in 2026 are going to be absolutely legendary. Ready for it!",
    "Unreal experience today at the #TrophyTour with @CocaCola. Holding back tears, feeling #AllTheFeels right now ❤️⚽",
    "Who do you think is lifting the trophy in 2026? Drop your predictions below! 👇🏆 #FIFAWorldCup26",
    "¡Increíble ambiente hoy en la Ciudad de México! El Trofeo Original de la Copa Mundial de la FIFA está en casa. La pasión se siente en el aire 🇲🇽⚽",
    "Such an honor to welcome the football legend Gilberto Silva and see this beautiful icon in person! Unforgettable event. @CocaCola",
    "El fútbol se vive cada día más intenso. En la tierra de los campeones, ver la copa de cerca es un sueño hecho realidad. 🇦🇷🏆",
    "Who is excited for the biggest sporting event in history? USA, Mexico, and Canada are not ready for this hype! 🔥",
    "Spotted the iconic trophy up close today at Sunway Pyramid! Thanks to @CocaCola for bringing this magic closer to fans.",
    "Ticket giveaway for the next stadium stop is officially open! Make sure to check the link in our bio to win exclusive VIP passes! 🎟️✨"
]

# תבניות תוכן מתוחכמות (חטיפה סמנטית - נראה קשור במבט ראשון, אבל המטרה שונה)
hijack_templates = [
    "Can't wait for summer 2026! Speaking of heat, our new summer sneaker collection just dropped ⚡ Link in bio for 20% off today only!",
    "The energy around the world cup is crazy right now. Perfect time to talk about how the global markets are moving. Check my pinned post for a breakdown of top trading setups this week 📈",
    "Everyone is out here looking for World Cup tickets but honestly I'm just trying to find the best tacos in CDMX 😂 Hit me up with recommendations!",
    "Throwback to last summer's road trip. Planning the next one for 2026 to catch some matches live. Where should we stop?",
    "Prepping for the big game requires the right fuel. Today's high-protein meal prep is locked in. Recipe on my broadcast channel! 💪",
    "The FIFA trophy looks so shiny in person, reminds me of the premium finish on the new phone cases we just added to the shop. Link in bio!",
    "Who else is ignoring all their responsibilities today just to watch sports content? Guilty as charged 🙋‍♂️"
]

def generate_post_id():
    return str(random.randint(3700000000000000000, 3950000000000000000))

def generate_timestamp():
    start_date = datetime(2025, 11, 15)
    random_days = random.randint(0, 180)
    random_seconds = random.randint(0, 86400)
    dt = start_date + timedelta(days=random_days, seconds=random_seconds)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")

posts_data = []
target_hashtags_list = ["#TrophyTour", "#FIFAWorldCup", "#CocaCola", "#AllTheFeels", "#FIFAWorldCup26"]
hashtags_str_formatted = ", ".join(target_hashtags_list)

for i in range(TOTAL_POSTS):
    is_spam = random.random() < SPAM_RATIO
    post_id = generate_post_id()
    timestamp = generate_timestamp()
    target_hashtag = random.choice(["TrophyTour", "FIFAWorldCup26", "CocaCola"])
    
    if is_spam:
        username = random.choice(USERNAMES_HIJACK)
        base_content = random.choice(hijack_templates)
        
        # לפעמים ההאשטאגים מעורבבים עם תגיות טרנדיות אחרות באופן טבעי
        if random.random() < 0.4:
            content = f"{base_content} {' '.join(target_hashtags_list)} #summer2026 #lifestyle"
        else:
            content = f"{base_content} {' '.join(target_hashtags_list)}"
            
        # רוכבי טרנדים מתוחכמים מקבלים לייקים אורגניים כי הם לא בוטים קלאסיים
        num_likes = random.randint(40, 1200)
        num_comments = random.randint(2, 45)
    else:
        username = random.choice(USERNAMES_LEGIT)
        base_content = random.choice(legit_templates)
        
        # הכנסת "לכלוך אנושי" לפוסטים הלגיטימיים (שגיאות כתיב קלות, סלנג)
        if random.random() < 0.3:
            base_content = base_content.replace("believe", "belive").replace("beautiful", "beautifull").replace("🏆", "🏆🏆🏆")
            base_content += " Omg so hyped!!!!"
            
        content = f"{base_content} {' '.join(target_hashtags_list)}"
        num_likes = random.randint(120, 35000)
        num_comments = random.randint(3, 850)
    
    clean_content = content.replace('\n', ' ')
    
    posts_data.append([
        target_hashtag,
        post_id,
        username,
        hashtags_str_formatted,
        timestamp,
        clean_content,
        num_likes,
        num_comments
    ])

# שמירה ל-CSV
headers = ["target_hashtag", "post_id", "username", "hashtags", "timestamp", "content", "num_likes", "num_comments"]
with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(headers)
    writer.writerows(posts_data)