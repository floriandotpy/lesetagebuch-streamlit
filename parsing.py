from typing import List
import pandas as pd


def author_gender(tags):
    gender_tags = {
        'author_m': 'Male',
        'author_f': 'Female',
        'author_d': 'Diverse / Multiple',
    }
    for tag in tags:
        if tag.lower() in gender_tags:
            return gender_tags[tag]
    return 'Unknown'

def language(tags):
    for lang in ('German', 'English'):
        if lang.lower() in tags:
            return lang
    return 'Unknown'

def genre(tags):
    nonfiction_tags = [
        'nonfiction',
        'history',
        'finance',
        'science',
        'ww2',
        'business',
        'biography',
        'coding',
        'philosophy',
        'feminism']
    fiction_tags = [
        'fiction',
        'novel',
        'fantasy']
    
    if any(t in tags for t in nonfiction_tags):
        return 'nonfiction'
    if any(t in tags for t in fiction_tags):
        return 'fiction'
    
    return 'unknown'

def json_to_dataframe(books: List[dict]) -> pd.DataFrame:

    drop_keys = ['book', 'user']
    books_flat = [
        {
            **{k:v for k, v in book.items() if k not in drop_keys},
            **{
                'author': book['book']['authors'][0]['name'],
                'title': book['book']['title'],
                'book_pages': book['book']['pages'],
                'username': book['user']['username'],
                'language': language(book.get('tags')),
                'author_gender': author_gender(book.get('tags')),
                'genre': genre(book.get('tags'))
            }
        }
        for book in books['entries']
    ]

    df = pd.DataFrame(books_flat)
    df['date'] = df.date.str.replace('00', '01')  # fallback dates were day not specified
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

    # ignore 'wished' items
    df = df[df.type=='finished']

    return df
