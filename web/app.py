# app.py

import streamlit as st
import os
import time
from datetime import datetime
from os.path import join as pjoin
from config import PROJECT_NAME, TASKS_ROOT

# Helper function to get folders in a given directory
def get_folders(directory):
    return [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]

# Navigation
def go_home():
    st.session_state.page = "Home"
    st.session_state.task = None
    st.session_state.model = None
    st.session_state.answer_files=None
    st.session_state.selected_answer_file=None

def fetch_history():
    questions_root_path = pjoin(TASKS_ROOT, st.session_state.task, st.session_state.model)
    return os.listdir(questions_root_path)

def go_to_page(page, task=None, model=None):
    st.session_state.page = page
    if task:
        st.session_state.task = task
    if model:
        st.session_state.model = model  

def create_new_question(question_id, input_text, upload_file):
    question_path = pjoin(TASKS_ROOT, st.session_state.task, st.session_state.model, question_id)
    os.makedirs(question_path, exist_ok=True)
    st.session_state.question_id = question_id
    if input_text:
        with open(pjoin(question_path, "input_text.txt"), 'w') as f:
            f.write(input_text)
    if upload_file:
        with open(pjoin(question_path, upload_file.name), 'wb') as f:
            f.write(upload_file.getbuffer())
    st.session_state.page = "Rendering"

def review_question(question_id):
    question_path = pjoin(TASKS_ROOT, st.session_state.task, st.session_state.model, question_id)
    st.session_state.question_id = question_id
    st.session_state.answer_files = os.listdir(question_path)
    st.session_state.page = "Answer Display"

# Initialization
if 'page' not in st.session_state:
    st.session_state.page = "Home"
if 'task' not in st.session_state:
    st.session_state.task = None
if 'model' not in st.session_state:
    st.session_state.model = None

# Pages
if st.session_state.page == "Home":
    st.title(PROJECT_NAME)
    st.button("Enter", on_click=lambda: go_to_page("Task Selection"))
elif st.session_state.page == "Task Selection":
    st.button("Home", on_click=go_home)
    st.title("Task Selection")
    tasks = get_folders(TASKS_ROOT)
    cols = st.columns(2)
    for i, task in enumerate(tasks):
        with cols[i % 2]:
            st.button(task, on_click=lambda task=task: go_to_page("Model Selection", task=task))
elif st.session_state.page == "Model Selection":
    st.button("Home", on_click=go_home)
    st.title("Model Selection")
    selected_task = st.session_state.task
    models = get_folders(pjoin(TASKS_ROOT, selected_task))
    cols = st.columns(2)
    for i, model in enumerate(models):
        with cols[i % 2]:
            st.button(model, on_click=lambda model=model: go_to_page("Problem Create", model=model))
    
elif st.session_state.page == "Problem Create":
    cols = st.columns(2)
    with cols[0]:
        st.button("Home", on_click=go_home)
    with cols[1]:
        st.button("History", on_click=lambda: go_to_page("History Review"))
    st.title("Problem Create")
    question_id = datetime.now().strftime('%Y%m%d %H%M%S')
    st.write("question_id: ", question_id)
    upload_file=None
    input_text = st.text_area("Input Text", disabled=bool(upload_file))
    upload_file = st.file_uploader("Upload File", disabled=bool(input_text))
    st.button("Submit", on_click=lambda: create_new_question(question_id, input_text, upload_file))
elif st.session_state.page == "Rendering":
    st.button("Home", on_click=go_home)
    st.title("Rendering")
    st.write("  \n")
    st.write("  \n")
    loading_progress_bar = st.progress(0)
    for percent_complete in range(100):
        time.sleep(0.03)
        loading_progress_bar.progress(percent_complete + 1)
    time.sleep(0.5)
    question_path = pjoin(TASKS_ROOT, st.session_state.task, st.session_state.model, st.session_state.question_id)
    while True:
        answer_files = os.listdir(question_path)
        if answer_files:
            st.session_state.answer_files = answer_files
            st.session_state.page = "Answer Display"
            st.rerun()
        time.sleep(1)
elif st.session_state.page == "Answer Display":
    st.button("Home", on_click=go_home)
    st.title("Answer Display")
    selected_file = st.selectbox("Select Answer File", st.session_state.answer_files)
    if selected_file is not None:
        st.session_state.selected_answer_file = selected_file
    with open(pjoin(TASKS_ROOT, st.session_state.task, st.session_state.model, st.session_state.question_id, st.session_state.selected_answer_file), "r") as f:
        answer_text = f.read()
    st.code(answer_text, language="markdown")
elif st.session_state.page == "History Review":
    cols = st.columns(2)
    with cols[0]:
        st.button("Home", on_click=go_home)
    with cols[1]:
        st.button("Ask Question", on_click=lambda: go_to_page("Problem Create"))
    st.title("History Review")
    history_questios=fetch_history()
    for question_id in history_questios:
        st.button(question_id, on_click=lambda question_id=question_id: review_question(question_id))