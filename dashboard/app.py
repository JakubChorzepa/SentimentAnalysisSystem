import streamlit as st

st.set_page_config(page_title="Panel analizy klasyfikacji problemów psychicznych", layout="wide")

import pandas as pd
import psycopg2
import plotly.express as px
from plotly.colors import qualitative
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

refresh_interval = 60000
st_autorefresh(interval=refresh_interval, key="auto_refresh")

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="reddit_db",
        user="reddit_user",
        password="reddit_pass",
        port=5440
    )

# Nagłówek aplikacji
st.title("🧠 Panel analizy klasyfikacji problemów psychicznych")
st.markdown("Analiza postów Reddit pod kątem problemów zdrowia psychicznego")

categories = [
    "Anxiety", "Bipolar", "Depression",
    "Normal", "Personality disorder", "Stress", "Suicidal"
]

CATEGORY_COLORS = {
    category: qualitative.Pastel[i]
    for i, category in enumerate(categories)
}

# Pobieranie danych
@st.cache_data(ttl=30)
def load_data():
    conn = get_db_connection()
    query = """
    SELECT id, title, text, created_utc, subreddit, sentiment_label, sentiment_score
    FROM mental_health_posts
    ORDER BY created_utc DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    
    if not df.empty:
        df['created_utc'] = pd.to_datetime(df['created_utc'])
        df['date'] = df['created_utc'].dt.date
    return df

df = load_data()

# Sekcja metryk
st.subheader("Podsumowanie danych")
if not df.empty:
    total_posts = len(df)
    top_category = df['sentiment_label'].value_counts().index[0] if 'sentiment_label' in df else 'N/A'
    top_category_perc = df['sentiment_label'].value_counts(normalize=True).iloc[0] * 100
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Łącznie postów", total_posts)
    col2.metric("Najczęstsza kategoria", top_category)
    col3.metric("Udział najczęstszej kategorii", f"{top_category_perc:.1f}%")
else:
    st.warning("Brak danych do wyświetlenia")

# Filtr danych
st.sidebar.header("Filtry")
if not df.empty:
    all_categories = sorted(df['sentiment_label'].unique())
    all_subreddits = sorted(df['subreddit'].unique())
    
    selected_categories = st.sidebar.multiselect(
        "Kategorie problemów",
        options=all_categories,
        default=all_categories
    )
    
    selected_subreddits = st.sidebar.multiselect(
        "Subreddity",
        options=all_subreddits,
        default=all_subreddits
    )
    
    min_date = df['date'].min()
    max_date = df['date'].max()
    date_range = st.sidebar.date_input(
        "Zakres dat",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    if len(date_range) == 2:
        filtered_df = df[
            (df['sentiment_label'].isin(selected_categories)) &
            (df['subreddit'].isin(selected_subreddits)) & 
            (df['date'] >= date_range[0]) &
            (df['date'] <= date_range[1])
        ]
    else:
        filtered_df = df
        st.sidebar.warning("Wybierz pełny zakres dat")
else:
    filtered_df = pd.DataFrame()

# Wizualizacje
if not filtered_df.empty:
    st.subheader("Rozkład kategorii problemów")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Wykres kołowy
        category_counts = filtered_df['sentiment_label'].value_counts().reset_index()
        category_counts.columns = ['category', 'count']
        
        fig_pie = px.pie(
            category_counts, 
            names='category', 
            values='count',
            color='category',
            hole=0.3,
            color_discrete_map=CATEGORY_COLORS
        )
        fig_pie.update_layout(showlegend=True)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Wykres słupkowy
        fig_bar = px.bar(
            category_counts, 
            x='category', 
            y='count',
            color='category',
            text='count',
            color_discrete_map=CATEGORY_COLORS
        )
        fig_bar.update_layout(
            xaxis_title="Kategoria problemu",
            yaxis_title="Liczba postów",
            showlegend=False
        )
        fig_bar.update_traces(textposition='outside')
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Analiza jakości klasyfikacji
    st.subheader("Analiza jakości klasyfikacji")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Rozkład pewności klasyfikacji
        fig_confidence = px.histogram(
            filtered_df, 
            x='sentiment_score',
            nbins=20,
            color_discrete_sequence=['#636EFA']
        )
        fig_confidence.update_layout(
            xaxis_title="Pewność klasyfikacji",
            yaxis_title="Liczba postów"
        )
        st.plotly_chart(fig_confidence, use_container_width=True)
    
    with col2:
        # Średnia pewność per kategoria
        avg_confidence = filtered_df.groupby('sentiment_label')['sentiment_score'].mean().reset_index()
        avg_confidence.columns = ['category', 'avg_score']
        avg_confidence = avg_confidence.sort_values('avg_score', ascending=False)
        
        fig_avg_conf = px.bar(
            avg_confidence, 
            x='avg_score', 
            y='category',
            orientation='h',
            text_auto='.3f',
            color_discrete_sequence=['#00CC96']
        )
        fig_avg_conf.update_layout(
            xaxis_title="Średnia pewność klasyfikacji",
            yaxis_title="Kategoria",
            showlegend=False
        )
        st.plotly_chart(fig_avg_conf, use_container_width=True)
    
    # Przegląd postów
    st.subheader("Przegląd postów")
    
    selected_category = st.selectbox(
        "Wybierz kategorię do przeglądu:",
        options=all_categories
    )
    
    category_posts = filtered_df[filtered_df['sentiment_label'] == selected_category]
    
    if not category_posts.empty:
        st.markdown(f"**Liczba postów w kategorii '{selected_category}':** {len(category_posts)}")
        
        # Najbardziej pewne klasyfikacje
        st.markdown("**Najbardziej pewne klasyfikacje:**")
        top_confident = category_posts.nlargest(3, 'sentiment_score')
        
        for i, row in top_confident.iterrows():
            with st.expander(f"{row['title']} (pewność: {row['sentiment_score']:.2f})"):
                st.markdown(f"**Subreddit:** r/{row['subreddit']}")
                st.markdown(f"**Klasyfikacja:** {row['sentiment_label']}")
                st.markdown(f"**Data:** {row['created_utc']}")
                st.markdown(f"**Tekst:**")
                st.write(row['text'][:500] + "..." if len(row['text']) > 500 else row['text'])
    
        # Najnowsze posty
        st.markdown("**Najnowsze posty:**")
        latest_posts = category_posts.head(5)
        
        for i, row in latest_posts.iterrows():
            with st.expander(f"{row['title']} ({row['created_utc'].strftime('%Y-%m-%d')})"):
                st.markdown(f"**Pewność klasyfikacji:** {row['sentiment_score']:.2f}")
                st.markdown(f"**Klasyfikacja:** {row['sentiment_label']}")
                st.markdown(f"**Subreddit:** r/{row['subreddit']}")
                st.markdown(f"**Tekst:**")
                st.write(row['text'][:500] + "..." if len(row['text']) > 500 else row['text'])
    else:
        st.info(f"Brak postów w kategorii '{selected_category}' dla wybranych filtrów")

else:
    st.warning("Brak danych spełniających kryteria filtrów")

# Informacje o modelu
st.sidebar.header("Informacje o modelu")
st.sidebar.markdown("""
**Mapowanie klas:**
- 0: Anxiety (Lęk)
- 1: Bipolar (Choroba afektywna dwubiegunowa)
- 2: Depression (Depresja)
- 3: Normal (Bez problemów)
- 4: Personality disorder (Zaburzenia osobowości)
- 5: Stress (Stres)
- 6: Suicidal (Myśli samobójcze)
""")
st.sidebar.markdown(f"**Ostatnia aktualizacja danych:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# Uruchomienie
if __name__ == "__main__":
    st.write("Dashboard aktywny")