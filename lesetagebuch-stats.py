from typing import List
import streamlit as st
import pandas as pd
import json

from parsing import json_to_dataframe, language


username = st.text_input("Lesetagebuch user name:")

if not username:
    st.error("Bitte gib oben deinen Usernamen von Lesetagebuch ein")
    st.stop()

st.write(f"Profil von {username}")


@st.cache
def fetch_profile(username: str):
    url = f"https://lesetagebu.ch/von/{username}.json"
    return pd.read_json(url)


books = fetch_profile(username)

# with open("florian.json") as fp:
#     books = json.load(fp)

df = json_to_dataframe(books)

st.header("All books")
df


st.header("Books per year")
yearly_stats = (
    df.assign(year=lambda entry: entry['date'].dt.year
              ).groupby('year')[['title', 'book_pages']]
).agg({
    'title': 'count',
    'book_pages': 'sum'})
st.table(yearly_stats)

st.bar_chart(
    yearly_stats['title'].sort_index(ascending=False)
)

st.header("Pages per year")
st.bar_chart(
    yearly_stats['book_pages'].sort_index(ascending=False)
)


st.header("Which is the busiest reading month?")
years = df.assign(
    year=lambda entry: entry['date'].dt.year
)['year']
num_years = len(years.unique())
st.write(f"In total, you have logged books in **{num_years} years** now.")

monthly_stats = (
    df.assign(
        month=lambda entry: entry['date'].dt.month
    )
    .groupby('month')[['title', 'book_pages']]
).agg({
    'title': 'count',  # FIXME: I need the mean of the count instead!
    'book_pages': 'mean'
}).rename(
    columns={
        'title': 'books_num_total',
        'book_pages': 'pages_per_month'
    }
).assign(
    books_per_month=lambda entry: (entry['books_num_total'] / num_years)
)[
    ['pages_per_month', 'books_per_month']
]

num_to_month = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December"
}
busiest_month_idx = monthly_stats['books_per_month'].idxmax()

st.write(
    f"You appear to read most pages in the month of **{num_to_month.get(busiest_month_idx, '?')}**.")
st.bar_chart(
    monthly_stats['books_per_month'].sort_index()
)

st.header("Book ratings")
df_rated = (df[df.rating.notnull()][df.rating > 0])
st.bar_chart(
    df_rated.rating.value_counts().sort_index()
)

st.header("Book languages")
df_language = pd.pivot_table(
    df.assign(
        year=lambda entry: entry['date'].dt.year
    ),
    index='year',
    columns='language',

    # count number of books (=number of titles)
    values='title',
    aggfunc='count',

    # prepare so that we can calculate percentages in next step
    # fill_value=0,
    # margins=True
).fillna(0)
languages = [l for l in df.language.unique()]
df_language["All"] = df_language[languages].sum(axis=1)
st.table(df_language)

df_language_percent = df_language.div(df_language.All, axis=0)[languages]
df_language_percent

st.table(df_language_percent)

# following somehow causes error
# st.bar_chart(
#     df_language_percent,
# )
