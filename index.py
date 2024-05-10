import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def crawl_vnexpress(num_pages):
    base_url = "https://vnexpress.net/"
    all_articles = []

    for page_num in range(1, num_pages + 1):
        url = f"{base_url}/p{page_num}"
        response = requests.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.find_all('h3', class_='title-news')
            
            for article in articles:
                title = article.text.strip()
                link = article.a['href']
                description_elem = article.find_next_sibling('p', class_='description')
                description = description_elem.text.strip() if description_elem else None
                all_articles.append({"title": title, "link": link, "description": description})
        else:
            st.error(f"Không thể truy cập trang {page_num}. Đang bỏ qua...")

    return all_articles

def search_articles(all_articles, query):
    search_results = []
    for article in all_articles:
        if query.lower() in article['title'].lower():
            search_results.append(article)
    return search_results


def main():
    st.title("Trình cào web VnExpress")

    if 'all_data' not in st.session_state:
        st.session_state.all_data = []

    num_pages_to_crawl = st.sidebar.number_input("Nhập số trang muốn cào:", min_value=1, value=5)
    if st.sidebar.button("Cào"):
        st.info("Đang cào dữ liệu... Vui lòng đợi.")
        all_data = crawl_vnexpress(num_pages_to_crawl)
        st.session_state.all_data = all_data  
        st.success(f"Đã cào thành công {len(all_data)} bài báo!")
        
    if len(st.session_state.all_data) > 0:
        st.write(pd.DataFrame(st.session_state.all_data))

    search_query = st.sidebar.text_input("Nhập từ khóa tìm kiếm:")
    if search_query:
        search_results = search_articles(st.session_state.all_data, search_query)
        st.write("Kết quả tìm kiếm:")
        if len(search_results) == 0:
            st.write("Không tìm thấy kết quả phù hợp.")
        else:
            st.write(pd.DataFrame(search_results))

if __name__ == "__main__":
    main()