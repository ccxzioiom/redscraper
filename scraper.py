import praw
import re
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk

# Download NLTK data (run once)
nltk.download('punkt')
nltk.download('stopwords')

# Reddit API Configuration
reddit = praw.Reddit(
    client_id='mkd5-McA7oBSnO1b5mtyqA',  # Replace with your client_id
    client_secret='#',  # Replace with your client_secret
    user_agent='#'  # Customize this for your app
)

# Load blacklist from external file
def load_blacklist(filename):
    with open(filename, 'r') as file:
        return set(line.strip().lower() for line in file.readlines())

# Load brand names from an external file
def load_brand_names(filename):
    with open(filename, 'r') as file:
        return set(line.strip().lower() for line in file.readlines())

# Load the custom blacklist and brand names
blacklist = load_blacklist('blacklist.txt')
brand_names = load_brand_names('brand_names.txt')

# Function to process subreddit
def process_subreddit(subreddit_name):
    # Subreddit Name
    post_limit = 1000  # Number of posts to scrape

    # Try to connect to the subreddit
    try:
        subreddit = reddit.subreddit(subreddit_name)
        print(f"Connected to subreddit: {subreddit.display_name}")
    except Exception as e:
        print(f"Failed to connect to subreddit: {e}")
        return

    # Initialize variables
    product_mentions = Counter()
    stop_words = set(stopwords.words('english'))

    # Process posts
    try:
        posts = subreddit.hot(limit=post_limit)  # Fetch 'hot' posts
        for post in posts:
            # Only process the post title
            title = post.title
            words = word_tokenize(title.lower())

            # Filter out words that are in the blacklist or stopwords and are not part of brand names
            filtered_words = []
            for i, word in enumerate(words):
                if word.isalnum() and word not in stop_words and len(word) > 2:
                    # Check for two-word brand names first
                    if i < len(words) - 1:
                        combined_word = f"{word} {words[i + 1]}"
                        if combined_word in brand_names:
                            filtered_words.append(combined_word)
                            continue

                    # If not a brand name, check if it's in the blacklist
                    if word not in blacklist:
                        filtered_words.append(word)

            # Add words to Counter
            product_mentions.update(filtered_words)

        # Optional: Filter product-like terms using a regex
        product_pattern = re.compile(r'[a-zA-Z]+\d*')  # Adjust this regex for specific product patterns
        filtered_products = Counter({k: v for k, v in product_mentions.items() if product_pattern.match(k)})

        # Display results
        print("\nMost Common Products:")
        for product, count in filtered_products.most_common(50):
            print(f"{product}: {count}")

    except Exception as e:
        print(f"Error while processing posts: {e}")

# Main loop to allow multiple subreddit inputs
while True:
    subreddit_name = input("Enter the subreddit name (or type 'exit' to quit): ")
    if subreddit_name.lower() == 'exit':
        break
    process_subreddit(subreddit_name)
