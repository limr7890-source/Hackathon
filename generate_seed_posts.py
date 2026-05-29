"""
Generate 100 realistic seed posts for the FIFA World Cup Trophy Tour campaign.
These represent genuine, high-quality campaign posts from verified users.
"""

import csv
import random
from datetime import datetime, timedelta


# Realistic usernames for campaign participants
USERNAMES = [
    "cocacola_official", "cocacola_malaysia", "fifaworldcup", "road_to_2026",
    "football_fever26", "soccer_mom_kl", "malaysia_sports_fan", "trophy_hunter",
    "world_cup_dreams", "football_fanatic_my", "soccer_enthusiast", "kl_football_club",
    "penang_soccer", "johor_football", "sabah_sports", "sarawak_united",
    "kuching_football", "ipoh_soccer_fan", "melaka_sports", "selangor_football",
    "putrajaya_sports", "cyberjaya_soccer", "petaling_jaya_fc", "subang_sports",
    "shah_alam_football", "klang_soccer", "ampang_football", "cheras_sports",
    "bukit_bintang_fc", "pavilion_sports", "sunway_football", "mid_valley_soccer"
]

# Realistic post content templates
CONTENT_TEMPLATES = [
    "¡Increíble ambiente hoy en {location}! El Trofeo Original de la Copa Mundial de la FIFA está en casa. La pasión se siente en el aire 🇲🇽⚽",
    "Unreal experience today at the #TrophyTour with @CocaCola. Holding back tears, feeling #AllTheFeels right now ❤️⚽",
    "Spotted the iconic trophy up close today at {location}! Thanks to @CocaCola for bringing this magic closer to fans.",
    "The FIFA World Cup Trophy is HERE in {location}! 🏆 Come celebrate with us at the #TrophyTour. Experience the magic of football history.",
    "Standing next to greatness. The World Cup Trophy Tour brought to you by Coca-Cola is absolutely incredible! Can't wait for 2026! 🇨🇦🇲🇽🇺🇸",
    "Dreams do come true! Got to see the FIFA World Cup Trophy in person today. Thank you @CocaCola for this once-in-a-lifetime opportunity! ⚽🏆",
    "The energy at the Trophy Tour today was INSANE! So many passionate football fans united by one dream.",
    "Brought my kids to see the World Cup Trophy today. Their faces lit up! This is what football is all about - bringing families together. Thank you Coca-Cola! 👨‍👩‍👧‍👦⚽",
    "Speechless. Just saw the actual FIFA World Cup Trophy. This is a moment I'll never forget. #TrophyTour",
    "The trophy is even more beautiful in person! Thank you @CocaCola for making this dream come true! 🏆✨",
    "Can't believe I'm standing next to the World Cup Trophy! This is surreal! 🤩⚽",
    "History in the making! The Trophy Tour is here and it's absolutely magical! ⚽🏆",
    "Feeling blessed to witness this iconic trophy up close. Football unites us all! 🌍⚽",
    "The atmosphere here is electric! Everyone's so excited about the Trophy Tour! ⚡🏆",
    "This is what dreams are made of! Thank you Coca-Cola for bringing the trophy to {location}! 🙏⚽",
    "My heart is racing! Just touched the World Cup Trophy! Best day ever! ❤️🏆",
    "The trophy tour is absolutely incredible! If you haven't been yet, GO! You won't regret it! 🏆✨",
    "Celebrating football history today at the Trophy Tour! What an amazing experience! 🎉⚽",
    "The World Cup Trophy is more stunning than I imagined! Thank you @CocaCola! 😍🏆",
    "Football fever is real! The Trophy Tour has everyone buzzing with excitement! ⚽🔥",
    "Honored to be part of this historic moment. The trophy is finally here! 🏆🙌",
    "This is why we love football! The Trophy Tour brings everyone together! ⚽❤️",
    "Pinch me, I must be dreaming! Just saw the FIFA World Cup Trophy! 😱🏆",
    "The trophy tour exceeded all my expectations! Absolutely phenomenal! 🌟⚽",
    "Football is more than a game, it's a passion! Thank you for this experience! ⚽💙"
]

# Locations
LOCATIONS = [
    "Sunway Pyramid", "Pavilion KL", "Mid Valley", "KLCC", "1 Utama",
    "Kuala Lumpur", "Penang", "Johor Bahru", "Ipoh", "Melaka",
    "Kuching", "Kota Kinabalu", "Shah Alam", "Petaling Jaya", "Subang Jaya"
]

# Hashtag combinations
HASHTAG_COMBOS = [
    "#TrophyTour, #FIFAWorldCup, #CocaCola, #AllTheFeels",
    "#TrophyTour, #FIFAWorldCup, #AllTheFeels",
    "#TrophyTour, #CocaCola, #AllTheFeels",
    "#FIFAWorldCup, #TrophyTour, #CocaCola",
    "#AllTheFeels, #TrophyTour, #FIFAWorldCup",
    "#CocaCola, #TrophyTour, #AllTheFeels",
    "#FIFAWorldCup, #AllTheFeels, #TrophyTour",
    "#TrophyTour, #FIFAWorldCup, #CocaCola, #AllTheFeels, #Malaysia",
]


def generate_seed_posts(num_posts=100, output_file="seed_posts.csv"):
    """Generate realistic seed posts."""
    
    posts = []
    start_date = datetime(2026, 1, 1)
    
    for i in range(num_posts):
        # Random date within campaign period (Jan 1 - Feb 20, 2026)
        days_offset = random.randint(0, 50)
        post_date = start_date + timedelta(days=days_offset)
        timestamp = post_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        
        # Generate post ID (realistic Instagram ID)
        post_id = 3700000000000000000 + random.randint(1, 200000000000000000)
        
        # Random username
        username = random.choice(USERNAMES)
        
        # Random content with location
        content_template = random.choice(CONTENT_TEMPLATES)
        location = random.choice(LOCATIONS)
        content = content_template.format(location=location)
        
        # Random hashtags
        hashtags = random.choice(HASHTAG_COMBOS)
        
        # Random engagement (likes and comments)
        # Seed posts should have good engagement
        num_likes = random.randint(5000, 50000)
        num_comments = random.randint(100, 1000)
        
        # Generate URL
        url = f"https://www.instagram.com/p/{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.choice('abcdefghijklmnopqrstuvwxyz')}{random.randint(1000, 9999)}/"
        
        post = {
            "target_hashtag": "seed",
            "post_id": post_id,
            "username": username,
            "hashtags": hashtags,
            "timestamp": timestamp,
            "content": content,
            "num_likes": num_likes,
            "num_comments": num_comments,
            "url": url,
            "score": 1
        }
        
        posts.append(post)
    
    # Write to CSV
    fieldnames = [
        "target_hashtag", "post_id", "username", "hashtags",
        "timestamp", "content", "num_likes", "num_comments", "url", "score"
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(posts)
    
    print(f"✅ Generated {num_posts} seed posts")
    print(f"   Output: {output_file}")
    print(f"\nSample posts:")
    for i, post in enumerate(posts[:3]):
        print(f"\n{i+1}. @{post['username']}")
        print(f"   {post['content'][:80]}...")
        print(f"   Likes: {post['num_likes']:,} | Comments: {post['num_comments']:,}")
    
    return posts


if __name__ == "__main__":
    generate_seed_posts(100, "seed_posts.csv")
