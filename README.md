# Research Paper Analysis QA Agent

This project is a Research Paper Analysis tool built as a question-answering (QA) agent, allowing users to interact with and retrieve information from scientific papers. It supports answering questions, summarizing findings, and suggesting future research directions based on multiple research papers.

## Features

The QA agent offers the following functionalities:
1. **Ask a Question** - Users can ask questions related to a single paper or multiple papers, including questions about images, charts, and graphs.
2. **Summarize Papers** - Summarize findings from multiple papers within a specified timeframe.
3. **Generate Future Work Ideas** - Extract key insights and propose future research opportunities based on multiple papers.

The system dynamically accepts multiple paper inputs and returns structured answers, summaries, or future work suggestions.

## Project Structure

- **`RAGPipeline`** (in `qa_agent.py`): The main class that handles downloading and extracting text from PDFs, embedding and retrieving text chunks, and generating answers.
- **Backend API**: A set of endpoints for answering questions, summarizing papers, and generating future work ideas.
- **Frontend**: A Streamlit-based user interface for interacting with the system, allowing users to input multiple papers, ask questions, and retrieve responses from the QA agent.

## Installation

### 1. Clone the Repository
   ```bash
   git clone https://github.com/your-username/research-paper-analysis-qa-agent.git
   cd research-paper-analysis-qa-agent
