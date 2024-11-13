
import requests
import os
import PyPDF2
import tempfile
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from db.db_init import Neo4jDatabase
db = Neo4jDatabase("bolt://localhost:7687", "neo4j", "Ashu@13016")


# Initialize the models
embedding_model_name = "all-MiniLM-L6-v2"
flan_t5_model_name = "google/flan-t5-base"

# Load the Sentence Transformer model for embeddings
embedding_model = SentenceTransformer(embedding_model_name)

# Load the FLAN-T5 model and tokenizer for text generation
tokenizer = AutoTokenizer.from_pretrained(flan_t5_model_name)
flan_t5_model = AutoModelForSeq2SeqLM.from_pretrained(flan_t5_model_name)

class RAGPipeline:
    def __init__(self, embedding_model_name="all-MiniLM-L6-v2", model_name="google/flan-t5-base"):
        # Load models
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.model_name = model_name

        # FAISS index to store embeddings
        self.index = None
        self.chunks_with_context = []

    def download_pdf(self, url):
        response = requests.get(url)
        response.raise_for_status()
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        temp_pdf.write(response.content)
        temp_pdf.close()
        return temp_pdf.name

    def extract_text_from_pdf(self, pdf_path):
        text_chunks = []
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                text_chunks.append((page_num, text))
        return text_chunks

    def chunk_text_with_context(self, text_chunks, chunk_size=512):
        self.chunks_with_context = []
        for page_num, text in text_chunks:
            words = text.split()
            for i in range(0, len(words), chunk_size):
                chunk_text = " ".join(words[i:i + chunk_size])
                self.chunks_with_context.append((page_num, chunk_text))

    def embed_chunks(self):
        embeddings = [self.embedding_model.encode(chunk[1]) for chunk in self.chunks_with_context]
        dimension = len(embeddings[0])
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(embeddings).astype('float32'))

    def retrieve_chunks_with_context(self, question, k=2):
        question_embedding = self.embedding_model.encode(question)
        _, indices = self.index.search(np.array([question_embedding]).astype('float32'), k)
        return [(self.chunks_with_context[i][0], self.chunks_with_context[i][1]) for i in indices[0]]

    def generate_answer_with_source(self, question, context_chunks):
        context = " ".join(chunk for _, chunk in context_chunks)
        input_text = f"Question: {question}\nContext: {context}\nAnswer:"

        # Generate answer using FLAN-T5
        inputs = tokenizer(input_text, return_tensors="pt", truncation=True, padding=True)
        outputs = flan_t5_model.generate(inputs["input_ids"], max_length=1024, num_beams=4, early_stopping=True)
        answer = tokenizer.decode(outputs[0], skip_special_tokens=True)

        heading = self.infer_heading_for_full_context(context)

        return {"answer": answer, "source_heading": heading}

    def infer_heading_for_full_context(self, context):
        input_text = f"Find the Heading name inside the following text:\n{context}\nHeading:"

        # Generate heading using FLAN-T5
        inputs = tokenizer(input_text, return_tensors="pt", truncation=True, padding=True)
        outputs = flan_t5_model.generate(inputs["input_ids"], max_length=100, num_beams=4, early_stopping=True)
        inferred_heading = tokenizer.decode(outputs[0], skip_special_tokens=True)

        return inferred_heading

    def summarize_across_papers(self, urls):
        summaries = []
        urls = [self.get_url_from_title(url) for url in urls]
        for url in urls:
            pdf_path = self.download_pdf(url)
            try:
                text_chunks = self.extract_text_from_pdf(pdf_path)
                self.chunk_text_with_context(text_chunks)
                context = " ".join(chunk[1] for chunk in self.chunks_with_context)
                input_text = f"Summarize the following text coherently:\n{context}\nSummary:"

                # Generate summary using FLAN-T5
                inputs = tokenizer(input_text, return_tensors="pt", truncation=True, padding=True)
                outputs = flan_t5_model.generate(inputs["input_ids"], max_length=1024, num_beams=4, early_stopping=True)
                summary = tokenizer.decode(outputs[0], skip_special_tokens=True)

                paper_name = url.split('/')[-1]  # Extract paper name from URL
                summaries.append({
                    "paper_name": paper_name,
                    "summary": summary
                })
            finally:
                os.remove(pdf_path)
        return {"summaries": summaries}

    def generate_future_work_ideas(self, urls):
        context = self.summarize_across_papers(urls)['summaries']
        context_text = "\n".join([f"Paper: {summary['paper_name']}\nSummary: {summary['summary']}" for summary in context])

        input_text = f"Based on the following research, suggest ideas for future work:\n{context_text}\nIdeas:"

        # Generate future work ideas using FLAN-T5
        inputs = tokenizer(input_text, return_tensors="pt", truncation=True, padding=True)
        outputs = flan_t5_model.generate(inputs["input_ids"], max_length=512, num_beams=4, early_stopping=True)
        ideas = tokenizer.decode(outputs[0], skip_special_tokens=True)

        return {"future_work_ideas": ideas}
    
    def get_url_from_title(self, title):
        url = db.get_url(title)
        url = f"{url}.pdf"
        url.replace("abs", "pdf")
        return url

    def answer_question_with_source(self, url, question, k=2):
        url = self.get_url_from_title(url)
        pdf_path = self.download_pdf(url)
        try:
            text_chunks = self.extract_text_from_pdf(pdf_path)
            self.chunk_text_with_context(text_chunks)
            self.embed_chunks()
            context_chunks = self.retrieve_chunks_with_context(question, k)
            answer_data = self.generate_answer_with_source(question, context_chunks)
            return {"answer": answer_data['answer'], "source_heading": answer_data['source_heading']}
        finally:
            os.remove(pdf_path)

    def answer_across_papers(self, question, urls, k=2):
        answers = []
        for url in urls:
            answer_data = self.answer_question_with_source(url, question, k)
            answers.append({"paper_url": url, "answer": answer_data['answer'], "source_heading": answer_data['source_heading']})
        return answers
