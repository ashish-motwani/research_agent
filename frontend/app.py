# frontend/app.py
import streamlit as st
import requests

backend_url = "http://localhost:8000"

st.title("Academic Research Assistant")

# Search Papers Section
st.header("Research Paper Finder")
st.write("Use this tool to search for research papers based on a topic and publication year range.")

# Input fields for topic and year range
topic = str(st.text_input("Enter Topic"))
year_from = str(st.number_input("Year From", min_value=2000, max_value=2024, step=1, value=2000))
year_to = str(st.number_input("Year To", min_value=2000, max_value=2024, step=1, value=2024))

# Search button
if st.button("Search"):
    # Parameters for API request
    params = {"topic": topic, "year_from": year_from, "year_to": year_to}

    # Fetch data from backend API
    response = requests.get(f"{backend_url}/get_papers/", params=params)
    papers = response.json().get("papers", [])

    # Display search results with clickable links
    if papers:
        st.subheader("Papers Found")
        for paper in papers:
            title, year, link = paper

            # Display title as a copyable code block
            st.code(title, language="")  # Display title for easy copying

            # Display year on a new line
            st.markdown(f"**Published Year:** {year}")

            # Display URL as a clickable link
            st.markdown(f"[Read Paper]({link})", unsafe_allow_html=True)

            # Add a divider for margin between papers
            st.markdown("<hr>", unsafe_allow_html=True)
    else:
        st.write("No papers found for the specified topic and year range.")



# Q&A section
st.header("Ask about a Paper")
paper_inputs = []

# State management for papers
if "paper_titles" not in st.session_state:
    st.session_state["paper_titles"] = [""]

# Function to add a new input field
def add_paper():
    st.session_state["paper_titles"].append("")

def ask_question(question, papers):
    if not papers:
        st.error("No papers provided!")
        return

    if len(papers) == 1:
        response = requests.get(
            f"{backend_url}/answer_question_single/",
            params={"question": question, "paper": papers[0]},
        )
    else:
        response = requests.post(
            f"{backend_url}/answer_question_multi/",
            json={"papers": papers, "question": question},  # Sending papers as JSON
        )

    return response.json().get("answer", "No answer available")

def summarize_papers(papers):
    if len(papers) == 1:
        response = requests.get(
            f"{backend_url}/summarize_paper_single/",
            params={"paper": papers[0]},
        )
    else:
        response = requests.post(
            f"{backend_url}/summarize_papers_multi/",
            json={"papers": papers},  # Sending papers as JSON
        )
    summaries = response.json().get("summaries", [])
    return "\n\n".join([f"Summary from {summary['paper_name']}:\n{summary['summary']}" for summary in summaries]) if summaries else "No summary available"

def generate_future_work(papers):
    if len(papers) == 1:
        response = requests.get(
            f"{backend_url}/generate_future_work_single/",
            params={"paper": papers[0]},
        )
    else:
        response = requests.post(
            f"{backend_url}/generate_future_work_multi/",
            json={"papers": papers},  # Sending papers as JSON
        )
    ideas = response.json().get("future_work_ideas", "")
    return ideas if ideas else "No future work ideas available"

# Display input fields for each paper
for i, title in enumerate(st.session_state["paper_titles"]):
    st.session_state["paper_titles"][i] = st.text_input(f"Paper Title {i + 1}", title)

# Button to add new paper input field
st.button("+ Add another paper", on_click=add_paper)

# Display a question input for Q&A
st.subheader("Ask a Question about the Papers")
question = st.text_input("Question")

# Ask question button
if st.button("Ask Question"):
    answer = ask_question(question, st.session_state["paper_titles"])
    st.write("Answer:", answer)

# Summarize button
st.subheader("Summarize Papers")
if st.button("Get Summary"):
    summary = summarize_papers(st.session_state["paper_titles"])
    st.write("Summary:", summary)

# Future work ideas button
st.subheader("Get Future Work Ideas")
if st.button("Get Future Work Ideas"):
    ideas = generate_future_work(st.session_state["paper_titles"])
    st.write("Future Work Ideas:", ideas)