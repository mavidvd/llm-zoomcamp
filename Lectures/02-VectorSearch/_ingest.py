import requests
from minsearch import Index
import time
from sqlitesearch import TextSearchIndex

def load_data():
    docs_url = "https://datatalks.club/faq/json/courses.json"
    response = requests.get(docs_url)
    courses_raw = response.json()

    documents = []
    url_prefix = "https://datatalks.club/faq"

    for course in courses_raw:
        course_url = f"""{url_prefix}{course["path"]}"""
        course_response = requests.get(course_url)
        course_response.raise_for_status()
        course_data = course_response.json()

        documents.extend(course_data)

    return documents

def build_index(documents):
    index = Index(
        text_fields=["question", "section", "answer"],
        keyword_fields=["course"]
    )
    index.fit(documents)
    return index

def load_db_knowledge_base(course = 'llm-zoomcamp'):

    documents = load_data()
    docs_llm = [doc for doc in documents if doc['course'] == course]
    index = TextSearchIndex(
        text_fields=["question", "section", "answer"],
        keyword_fields=["course"],
        db_path="kb.db"
    )

    for doc in docs_llm:
        index.add(doc)
        print(f"""Added: {doc["question"][:60]}...""")
        time.sleep(0.01)

    index.close()
    print("Done. Index saved to kb.db")
    return index