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
   ```

### 2. Install Dependencies
Install the required Python packages.

   ```bash
   pip install -r requirements.txt
   ```

### 3. Set Up Neo4j Database
Ensure you have a running instance of Neo4j on localhost:7687.
Set the username and password in db_init.py for the Neo4jDatabase class.

### 4. Configure Backend URL
Set the backend_url in the Streamlit frontend script to point to the address of your backend service (e.g., http://localhost:8000).

## Usage

### 1. Start the Backend Server
Ensure the backend API server is running, listening on the configured `backend_url`.

### 2. Run the Streamlit Frontend
Launch the Streamlit app with the following command:
```bash
streamlit run frontend_app.py
```

### 3. Interact with the QA Agent
Use the frontend to add multiple papers by clicking the **+ Add another paper** button. Enter questions, select functionalities, and retrieve responses from the QA agent.

## Backend Endpoints

### 1. Answer Question (/answer_question/)
- **Method:** GET
- **Parameters:** 
  - `question` 
  - `papers` (list of paper titles)
- **Response:** Answer to the question with context and source heading.

### 2. Summarize Papers (/summarize_papers/)
- **Method:** GET
- **Parameters:** 
  - `papers` (list of paper titles)
- **Response:** Summary of the findings across the specified papers.

### 3. Generate Future Work Ideas (/generate_future_work/)
- **Method:** GET
- **Parameters:** 
  - `papers` (list of paper titles)
- **Response:** Suggested future research directions based on the papers.

## Code Overview

### qa_agent.py
Contains `RAGPipeline`, a class that handles the core functionalities, including:
- **PDF Downloading and Text Extraction:** Downloads PDFs and extracts text for further processing.
- **Embedding and Indexing:** Embeds text chunks using sentence transformers and stores them in a FAISS index.
- **Context Retrieval:** Retrieves relevant text chunks to answer questions.
- **Answer Generation:** Uses a language model to generate answers and infer headings from relevant text.
- **Summarization:** Summarizes text across chunks for document summaries.
- **Future Work Generation:** Generates ideas for future research based on provided content.

### db_init.py
Initializes the connection to the Neo4j database used for storing and retrieving paper information. The credentials and database address are configurable.

### frontend_app.py
A Streamlit-based frontend application that:
- Accepts multiple paper inputs.
- Provides options for users to ask questions, summarize content, and generate ideas for future research.
- Displays responses from the backend server.

### requirements.txt
Lists the required Python libraries, including:
- **FAISS:** For efficient similarity search on embedded vectors.
- **Sentence Transformers:** For generating embeddings of text chunks.
- **Transformers:** For question-answering and summarization models.
- **Neo4j:** For database connections and querying paper metadata.

## Future Improvements
- **Enhanced PDF Parsing:** Add support for more complex table and image parsing within PDFs.
- **Increased Model Efficiency:** Optimize FAISS and LLM calls to improve response times.
- **Extended Summarization:** Add options for thematic or section-based summaries for more nuanced insights.
- **Improved Future Work Generation:** Enhance the model's capability to generate detailed and novel future research ideas by incorporating additional knowledge graphs or databases.

