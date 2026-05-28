import json
from datasets import load_dataset


def simulate_pipeline(
    target_topics,
    num_positives_to_generate=5,
    output_neg_file="final_hard_negatives.json",
    output_pos_file="simulated_positives.json",
):
    """
    גרסה סופית, יציבה ב-100% להאקתון - טוענת קובץ נתונים ישיר ללא קונפיגורציות בעייתיות.
    """

    # מיפוי נושאים ברור ויציב מתוך דאטאסט חדשות/ציוצים נפוץ (4 נושאים מרכזיים)
    topic_mapping = {0: "World", 1: "Sports", 2: "Business", 3: "Sci/Tech"}

    print("⏳ טוען דאטאסט מובנה ויציב (AG News) לצורך סימולציית הנושאים...")

    # זהו דאטאסט סופר פופולרי, נטען בשנייה בפורמט מודרני ללא שום שגיאות קונפיגורציה
    ds = load_dataset("ag_news")

    simulated_positives = []
    negatives_pool = []

    target_set = set(target_topics)

    for item in ds["train"]:
        label_id = item["label"]
        topic_name = topic_mapping.get(label_id)

        if not topic_name:
            continue

        # בדיקה אם הנושא הנוכחי הוא אחד מנושאי היעד (החיוביים)
        if topic_name in target_set:
            if len(simulated_positives) < num_positives_to_generate:
                simulated_positives.append(
                    {"text": item["text"], "label": [topic_name]}
                )
        else:
            # אם הוא שייך לנושא אחר לחלוטין -> נגטיב מעולה
            negatives_pool.append({"text": item["text"], "source_topics": [topic_name]})

    # 1. שמירת החיוביים הסינתטיים
    print(f"✨ נוצרו {len(simulated_positives)} הודעות חיוביות סינתטיות.")
    with open(output_pos_file, "w", encoding="utf-8") as f:
        json.dump(simulated_positives, f, ensure_ascii=False, indent=4)

    # 2. שמירת הנגטיבז
    print(f"🛑 נמצאו {len(negatives_pool)} הודעות שליליות ללא חפיפה.")
    with open(output_neg_file, "w", encoding="utf-8") as f:
        json.dump(negatives_pool, f, ensure_ascii=False, indent=4)

    print(f"💾 הקבצים נשמרו בהצלחה בתיקייה!")


if __name__ == "__main__":
    # הגדרת נושאים מתוך הרשימה: World, Sports, Business, Sci/Tech
    # לצורך הבדיקה נבחר ב-Sports וב-Sci/Tech כחיוביים
    test_topics = ["Sports", "Sci/Tech"]

    simulate_pipeline(
        target_topics=test_topics,
        num_positives_to_generate=10,
        output_pos_file="simulated_positives.json",
        output_neg_file="final_hard_negatives.json",
    )
