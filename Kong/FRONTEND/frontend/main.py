import streamlit as st
import requests
import os

# Define the FastAPI backend URL from the environment variable
backend_url = os.getenv("API_URL", "http://localhost:8000")

def fetch_todos():
    try:
        response = requests.get(f"{backend_url}/todos/")
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch todos: {e}")
        return []

def create_todo(content):
    todo = {"content": content}
    try:
        response = requests.post(f"{backend_url}/todos/", json=todo)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to create todo: {e}")
        return None

# Streamlit app
st.title("DR Comments")

# Input form for new todos
new_todo = st.text_input("Dr Comments")

if st.button("Add Comments"):
    if new_todo:
        created_todo = create_todo(new_todo)
        if created_todo:
            st.success(f"Todo added: {created_todo['content']}")
            st.experimental_rerun()  # Refresh the page to show the new todo
    else:
        st.error("Dr Comments Empty")

