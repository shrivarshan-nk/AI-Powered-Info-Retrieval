import streamlit as st
import requests
from transformers import pipeline
#import spacy

# Initialize the summarizer pipeline using Hugging Face Transformers
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

# Load spaCy model
#nlp = spacy.load("en_core_web_sm")

# Function to perform search using Google Custom Search API
def perform_search(query):
    api_key = 'AIzaSyAgKac39wfstboizc1StYGjqlT2rdQqVQ4'
    cx = "7394b4ca2ca1040ef"
    search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cx}"
    response = requests.get(search_url)
    return response.json()

# Function to summarize the overall combined content (make it longer)
def summarize_overall_content(content):
    if len(content) > 3000:  # Summarize up to 3000 characters for a larger summary
        content = content[:3000]
    summary = summarizer(content, max_length=300, min_length=100, do_sample=False)  # Larger overall summary
    return summary[0]['summary_text']

# Function to summarize individual search results (keep shorter)
def summarize_individual_content(content):
    if len(content) > 1000:  # Summarize first 1000 characters for brevity
        content = content[:1000]
    summary = summarizer(content, max_length=50, min_length=30, do_sample=False)  # Shorter summary
    return summary[0]['summary_text']

# Function to rank search results based on custom criteria
def rank_sources(results):
    # For now, assume sources are ranked by default order from API
    return results

# Function to extract related topics using spaCy
def extract_related_topics(query_list):
    related_topics = ["AI","ML"]
    related_topics.insert(0,"Deep Learning")
    return related_topics[:3]  # Limit to 3 related topics

# Function to display search results and summaries
def display_results(query):
    st.write(f"Searching for: {query}")
    
    # Perform search and get results
    search_results = perform_search(query)
    
    # Extract relevant items from search results
    if 'items' in search_results:
        ranked_results = rank_sources(search_results['items'])
        
        # Overall summary (bigger)
        st.write("### Overall Summary:")
        combined_content = " ".join([item['snippet'] for item in ranked_results])
        overall_summary = summarize_overall_content(combined_content)  # Use larger summary function
        st.write(overall_summary)
        
        # Individual results (shorter)
        st.write("### Individual Results:")
        for item in ranked_results:
            st.write(f"**[{item['title']}]({item['link']})**")
            st.write(summarize_individual_content(item['snippet']))  # Use shorter summary function
            st.write("---")
    else:
        st.write("No results found.")

# Main Streamlit App UI
st.title("AI-Powered Information Retrieval and Summarization")

# Initialize query list to store search queries
if 'querylist' not in st.session_state:
    st.session_state.querylist = []

# Search input by user
query = st.text_input("Enter your search query:")

# If query is provided, display results and update query list
if query:
    st.session_state.querylist.append(query)
    display_results(query)
    
    # Generate related topics based on query list
    related_topics = extract_related_topics(st.session_state.querylist)
    
    st.write("### Related Topics:")
    for topic in related_topics:
        st.write(f"- **[{topic}]({requests.utils.requote_uri(f'https://www.google.com/search?q={topic}')})**")

# Trending Topics Section with clickable links
st.sidebar.title("Trending Topics")
trending_topics = ["AI", "Machine Learning", "Sustainability", "Technology Trends"]
for idx, topic in enumerate(trending_topics):
    if st.sidebar.button(topic, key=f'topic_button_{idx}'):
        query = topic  # Automatically search for this topic when clicked

# Feedback Section (Visible after results)
if query or any(st.sidebar.button(topic) for topic in trending_topics):
    st.write("### Feedback")
    feedback = st.radio("Was this summary helpful?", ["Yes", "No"])
    if feedback == "Yes":
        st.write("Thank you for your feedback!")
    else:
        st.write("We will try to improve!")
