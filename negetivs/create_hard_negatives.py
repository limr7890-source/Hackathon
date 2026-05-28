from datasets import load_dataset


dataset = load_dataset("tweet_eval", "sentiment", split="train", streaming=True)


negative_candidates = []
for i, example in enumerate(dataset):
    if i >= 20000:
        break
    negative_candidates.append(example['text'])