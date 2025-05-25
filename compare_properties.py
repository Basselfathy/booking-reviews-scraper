import os
import pandas as pd
from collections import Counter
import re

#compareable files folder path
COMPAREABLE_FILES_FOLDER = os.path.join(os.path.dirname(__file__), 'output')

# Optional: nltk for better keyword extraction
try:
    import nltk
    from nltk.corpus import stopwords
    nltk.download('stopwords', quiet=True)
    STOPWORDS = set(stopwords.words('english'))
except ImportError:
    STOPWORDS = set()

def load_reviews(csv_path, date_col='review_post_date', start_date=None, end_date=None):
    df = pd.read_csv(csv_path)
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        if start_date:
            df = df[df[date_col] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df[date_col] <= pd.to_datetime(end_date)]
    return df

def get_sentiment_counts(df, rating_col='rating', threshold=7):
    # Simple rule: rating >= threshold is positive, else negative
    pos = df[df[rating_col] >= threshold]
    neg = df[df[rating_col] < threshold]
    return len(pos), len(neg), pos, neg

def extract_keywords(texts, top_n=10):
    words = []
    for text in texts:
        if pd.isna(text):
            continue
        # Remove punctuation, lowercase, split
        tokens = re.findall(r'\b\w+\b', str(text).lower())
        tokens = [w for w in tokens if w not in STOPWORDS and len(w) > 2]
        words.extend(tokens)
    return [w for w, _ in Counter(words).most_common(top_n)]

def compare_properties(csv_files, start_date, end_date):
    summary = []
    for csv_path in csv_files:
        # If the user provides e.g. 'property1/reviews_most_relevant.csv', always prepend the output folder
        full_csv_path = os.path.join('output', csv_path)
        property_name = os.path.basename(os.path.dirname(full_csv_path))
        df = load_reviews(full_csv_path, start_date=start_date, end_date=end_date)
        if df.empty:
            print(f"No reviews for {property_name} in selected date range.")
            continue
        pos_count, neg_count, pos_df, neg_df = get_sentiment_counts(df)
        avg_score = df['rating'].mean()
        avg_pos = pos_df['rating'].mean() if not pos_df.empty else None
        avg_neg = neg_df['rating'].mean() if not neg_df.empty else None
        pos_keywords = extract_keywords(pos_df['review_text_liked'])
        neg_keywords = extract_keywords(neg_df['review_text_disliked'])
        summary.append({
            'property': property_name,
            'total_reviews': len(df),
            'avg_score': round(avg_score, 2),
            'positive_reviews': pos_count,
            'negative_reviews': neg_count,
            'avg_positive_score': round(avg_pos, 2) if avg_pos else None,
            'avg_negative_score': round(avg_neg, 2) if avg_neg else None,
            'common_positive_keywords': ', '.join(pos_keywords),
            'common_negative_keywords': ', '.join(neg_keywords),
        })
    return pd.DataFrame(summary)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Compare multiple properties based on scraped reviews.')
    parser.add_argument('--csvs', nargs='+', required=True, help='Paths to review CSV files (one per property)')
    parser.add_argument('--start', type=str, required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, required=True, help='End date (YYYY-MM-DD)')
    parser.add_argument('--out', type=str, default='comparison_summary.csv', help='Output CSV file for summary')
    args = parser.parse_args()

    df = compare_properties(args.csvs, args.start, args.end)
    print(df.to_string(index=False))
    df.to_csv(args.out, index=False)
    print(f"\nSummary saved to {args.out}")

if __name__ == '__main__':
    main()
