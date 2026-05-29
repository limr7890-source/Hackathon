import pandas as pd

def get_mock_model_results():
    """
    Mock data generator with usernames for serial hijacker detection
    """
    data = {
        "Username": [
            "@nike_fan_2024", "@crypto_deals_247", "@football_lover", "@random_user_88", 
            "@bitcoin_master", "@fitness_journey", "@sports_fanatic", "@make_money_fast",
            "@runner_life", "@political_voice", "@marathon_prep", "@soccer_world",
            "@gym_motivation", "@free_stuff_daily", "@athlete_mindset", "@crypto_deals_247",
            "@make_money_fast", "@free_stuff_daily", "@bitcoin_master", "@authentic_user"
        ],
        "Target_Hashtag": [
            "#JustDoIt", "#JustDoIt", "#WorldCup", "#JustDoIt", "#WorldCup",
            "#JustDoIt", "#WorldCup", "#WorldCup", "#JustDoIt", "#WorldCup",
            "#JustDoIt", "#WorldCup", "#JustDoIt", "#WorldCup", "#JustDoIt",
            "#WorldCup", "#JustDoIt", "#JustDoIt", "#WorldCup", "#WorldCup"
        ],
        "Post_Text": [
            "Just finished my morning run! Loving the new shoes, perfect fit.",
            "Buy fake luxury watches for 90% off right now! Click here",
            "What a goal! The stadium is absolutely electric tonight!",
            "Look at my cute cat sleeping on the couch today, so adorable.",
            "Crypto flash sale! Double your coins in 24 hours link in bio",
            "No excuses. Pushing limits at the gym today.",
            "Amazing match, team played heart out, but we lost in penalties.",
            "Earn 5000$ a day working from home, guaranteed payout, DM me!",
            "New workout gear arrived, time to test it on the track!",
            "Unrelated political comment that has nothing to do with football.",
            "Training hard for the marathon next month. These shoes are incredible!",
            "Best game of the season! What a performance from the team!",
            "Morning workout complete. Feeling stronger every day.",
            "Click here for free iPhone giveaway! Limited time only!!!",
            "Pushed through 10K today. The grind never stops.",
            "Get rich quick with this one simple trick! DM now!",
            "Work from home and make thousands! No experience needed!",
            "Free money giveaway! Click the link in my bio now!",
            "Bitcoin to the moon! Buy now before it's too late!",
            "Great match today! The team really showed up!"
        ],
        "Likes": [1250, 3200, 8500, 45, 910, 2100, 6400, 1500, 890, 310, 1850, 7200, 1420, 2800, 1650, 4100, 3800, 5200, 2900, 6800],
        "Comments": [45, 810, 420, 2, 115, 88, 312, 430, 19, 75, 92, 580, 67, 920, 81, 650, 720, 890, 340, 410],
        "Model_Label": [1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1],
        "AI_Confidence": [0.94, 0.98, 0.96, 0.89, 0.99, 0.92, 0.91, 0.97, 0.93, 0.85, 0.95, 0.94, 0.90, 0.96, 0.93, 0.99, 0.98, 0.97, 0.99, 0.92],
        "Spam_Reason": [
            "Authentic fitness content",
            "Commercial spam - fake products",
            "Authentic sports content",
            "Off-topic content",
            "Crypto scam",
            "Authentic fitness content",
            "Authentic sports content",
            "Financial scam - work from home",
            "Authentic fitness content",
            "Off-topic - unrelated political content",
            "Authentic fitness content",
            "Authentic sports content",
            "Authentic fitness content",
            "Engagement farming - fake giveaway",
            "Authentic fitness content",
            "Financial scam",
            "Financial scam - work from home",
            "Engagement farming - fake giveaway",
            "Crypto scam",
            "Authentic sports content"
        ],
        "Estimated_Reach": [12500, 32000, 85000, 450, 9100, 21000, 64000, 15000, 8900, 3100, 18500, 72000, 14200, 28000, 16500, 41000, 38000, 52000, 29000, 68000]
    }
    
    df = pd.DataFrame(data)
    return df


if __name__ == "__main__":
    df_example = get_mock_model_results()
    print("--- Mock Data Sample ---")
    print(df_example)
