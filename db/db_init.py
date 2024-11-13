# db/db_init.py
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer, util

class Neo4jDatabase:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    def close(self):
        self.driver.close()

    def create_paper(self, title, year, topic, url):
        with self.driver.session() as session:
            session.run(
                "CREATE (p:Paper {title: $title, year: $year, topic: $topic, url: $url})",
                title=title, year=year, topic=topic, url=url
            )
    
    def delete_all_records(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def query_papers(self, topic, year_from=None, year_to=None):
        if topic:
            topic = topic.lower()
            print(topic)
            topic = self.find_most_similar_topic(topic)
            print(topic)

        with self.driver.session() as session:
            if topic and year_from and year_to:
                result = session.run(
                    "MATCH (p:Paper {topic: $topic}) WHERE $year_from <= p.year <= $year_to RETURN p.title, p.year, p.url",
                    topic=str(topic), year_from=str(year_from), year_to=str(year_to)
                )
            elif topic:
                result = session.run("MATCH (p:Paper {topic: $topic}) RETURN p.title, p.year, p.url", topic=str(topic))
            else:
                return None
            return [(record["p.title"], record["p.year"], record["p.url"]) for record in result]
    
    def get_url(self, title):
        with self.driver.session() as session:
            print(title)
            title = self.find_most_similar_title(title)
            print(title)
            result = session.run("MATCH (p:Paper {title: $title}) RETURN p.url", title=str(title))
            return result.single()[0]
    
    def get_stored_topics(self):
        """
        Retrieve stored topics from the Neo4j database.
        
        Returns:
            List of topics stored in the database.
        """
        with self.driver.session() as session:
            result = session.run("MATCH (p:Paper) RETURN DISTINCT p.topic AS name")
            topics = [record["name"] for record in result]
        return topics
    
    def find_most_similar_topic(self, input_topic, threshold=0.75):
        """
        Finds the most similar topic from the stored topics based on the input.
        
        Parameters:
            input_topic (str): The topic input by the user.
            threshold (float): Similarity threshold to consider a match.
        
        Returns:
            str or None: The most similar topic name or None if no match is found.
        """
        # Get all stored topics
        stored_topics = self.get_stored_topics()
        if stored_topics is None or len(stored_topics) == 0:
            return None

        # Embed the input topic
        input_embedding = self.embedder.encode(input_topic, convert_to_tensor=True)

        # Embed each stored topic
        stored_embeddings = self.embedder.encode(stored_topics, convert_to_tensor=True)

        # Compute cosine similarity
        similarities = util.pytorch_cos_sim(input_embedding, stored_embeddings).squeeze()

        # Find the best match above the threshold
        best_score = similarities.max().item()
        if best_score >= threshold:
            best_match_index = similarities.argmax().item()
            return stored_topics[best_match_index]
        else:
            return None
        
    def get_stored_titles(self):
        """
        Retrieve stored paper titles from the Neo4j database.
        
        Returns:
            List of paper titles stored in the database.
        """
        with self.driver.session() as session:
            result = session.run("MATCH (p:Paper) RETURN p.title AS title")
            titles = [record["title"] for record in result]
        return titles
    
    def find_most_similar_title(self, input_title, threshold=0.75):
        """
        Finds the most similar paper title from the stored titles based on the input.
        
        Parameters:
            input_title (str): The title input by the user.
            threshold (float): Similarity threshold to consider a match.
        
        Returns:
            str or None: The most similar title or None if no match is found.
        """
        # Get all stored titles
        stored_titles = self.get_stored_titles()
        if stored_titles is None or len(stored_titles) == 0:
            return None

        # Embed the input title
        input_embedding = self.embedder.encode(input_title, convert_to_tensor=True)

        # Embed each stored title
        stored_embeddings = self.embedder.encode(stored_titles, convert_to_tensor=True)

        # Compute cosine similarity
        similarities = util.pytorch_cos_sim(input_embedding, stored_embeddings).squeeze()

        # Find the best match above the threshold
        best_score = similarities.max().item()
        if best_score >= threshold:
            best_match_index = similarities.argmax().item()
            return stored_titles[best_match_index]
        else:
            return None
        
