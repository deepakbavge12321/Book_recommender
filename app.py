from flask import Flask, render_template, request
import pickle
import numpy as np
import json

app = Flask(__name__)

# Load pickled data
popular_df = pickle.load(open('popular.pkl', 'rb'))
pt = pickle.load(open('pt.pkl', 'rb'))
books = pickle.load(open('books.pkl', 'rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))

print("Type of popular_df:", type(popular_df))
print("Length of popular_df:", len(popular_df))
print("First few elements of popular_df:", popular_df[:5])

@app.route('/')
def index():
    # Check if popular_df is a list or a DataFrame
    if isinstance(popular_df, list):
        return "Error: popular_df is not loaded as a DataFrame"
    
    # Assuming popular_df is a DataFrame
    return render_template('index.html',
                           book_name=popular_df['Book-Title'].tolist(),
                           author=popular_df['Book-Author'].tolist(),
                           image=popular_df['Image-URL-M'].tolist(),
                           votes=popular_df['num_ratings'].tolist(),
                           rating=popular_df['avg_rating'].tolist()
                           )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')
    
    # Check if pt.index is empty
    if len(pt.index) == 0:
        return render_template('recommend.html', data=[], message="No books available for recommendation")

    index = np.where(pt.index == user_input)[0]
    
    # Check if the user input matches any book name
    if len(index) == 0:
        return render_template('recommend.html', data=[], message="Book not found")

    index = index[0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

        data.append(item)

    print(data)

    return render_template('recommend.html', data=data)


@app.route('/get_book_names', methods=['POST'])
def get_book_names():
    user_input = request.form.get('user_input')
    matching_books = [book for book in pt.index if user_input.lower() in book.lower()]
    return json.dumps(matching_books)
