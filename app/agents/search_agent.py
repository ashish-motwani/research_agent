# app/agents/search_agent.py
from db.db_init import Neo4jDatabase

db = Neo4jDatabase("bolt://localhost:7687", "neo4j", "Ashu@13016")

def add_paper(title, year, topic, url):
    db.create_paper(title, year, topic, url)

