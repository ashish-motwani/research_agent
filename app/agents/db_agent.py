# app/agents/db_agent.py
from db.db_init import Neo4jDatabase

db = Neo4jDatabase("bolt://localhost:7687", "neo4j", "Ashu@13016")

def fetch_papers_from_arxiv(topic):
    import requests
    # Perform search and parse results
    response = requests.get(f"https://export.arxiv.org/api/query?search_query={topic}")
    # Process response to extract relevant paper data
    parsed_papers = []
    for entry in response.text.split("<entry>")[1:]:
        title = entry.split("<title>")[1].split("</title>")[0]
        year = entry.split("<published>")[1].split("-")[0]
        url = entry.split("<id>")[1].split("</id>")[0]
        parsed_papers.append({"title": title, "year": year, "topic": topic, "url": url})
    return parsed_papers

def get_papers(topic=None, year_from=None, year_to=None):
    papers = db.query_papers(topic, year_from, year_to) 
    if papers:
        return papers
    
    # If no papers found in the database, fetch from ArXiv
    papers = fetch_papers_from_arxiv(topic)
    for paper in papers:
        db.create_paper(paper["title"], paper["year"], paper["topic"], paper["url"])

    papers = db.query_papers(topic, year_from, year_to)
    return papers

    




    
