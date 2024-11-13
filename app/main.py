# app/main.py
from app.agents import db_agent, qa_agent

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from app.agents.qa_agent import RAGPipeline

app = FastAPI()
qa_agent = RAGPipeline()

# Define a model to validate request bodies for multi-paper requests
class PapersRequest(BaseModel):
    papers: List[str]

# Route to fetch papers based on topic and year range
@app.get("/get_papers/")
async def get_papers(topic: str = None, year_from: int = None, year_to: int = None):
    papers = db_agent.get_papers(topic, year_from, year_to)
    return {"papers": papers}

# Route to answer a question based on a single paper
@app.get("/answer_question_single/")
async def answer_question(question: str, paper: str):
    answer_data = qa_agent.answer_question_with_source(paper, question)
    return {"answer": answer_data['answer'], "source_heading": answer_data['source_heading']}

# Route to answer a question across multiple papers
@app.post("/answer_question_multi/")
async def answer_question_multi(request: PapersRequest, question: str):
    papers = request.papers
    answer = qa_agent.answer_across_papers(question, papers)
    return {"answer": answer}

# Route to summarize a single paper
@app.get("/summarize_paper_single/")
async def summarize_paper(paper: str):
    summary_data = qa_agent.summarize_across_papers([paper])
    return {"summaries": summary_data['summaries']}

# Route to summarize multiple papers
@app.post("/summarize_papers_multi/")
async def summarize_papers(request: PapersRequest):
    papers = request.papers
    summary_data = qa_agent.summarize_across_papers(papers)
    return {"summaries": summary_data['summaries']}

# Route to generate future work ideas based on a single paper
@app.get("/generate_future_work_single/")
async def generate_future_work(paper: str):
    future_work_ideas = qa_agent.generate_future_work_ideas([paper])
    return {"future_work_ideas": future_work_ideas['future_work_ideas']}

# Route to generate future work ideas based on multiple papers
@app.post("/generate_future_work_multi/")
async def generate_future_work_multi(request: PapersRequest):
    papers = request.papers
    future_work_ideas = qa_agent.generate_future_work_ideas(papers)
    return {"future_work_ideas": future_work_ideas['future_work_ideas']}