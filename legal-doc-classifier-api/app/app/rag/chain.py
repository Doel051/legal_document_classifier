from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from .loaders import load_and_split_documents

class LegalRAGSystem:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.llm = ChatOpenAI(model="gpt-4-1106-preview", temperature=0.3)
        self.vector_store = None
        self.qa_chain = None
        
    def initialize_vector_store(self, docs):
        self.vector_store = Chroma.from_documents(
            documents=docs,
            embedding=self.embeddings,
            persist_directory="app/rag/vector_store"
        )
        self.vector_store.persist()
        
        prompt_template = """Use the following legal context to answer the question:
        {context}
        
        Question: {question}
        
        Answer in precise legal terms, citing relevant clauses when possible."""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(),
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
    
    def query(self, question):
        if not self.qa_chain:
            raise ValueError("Vector store not initialized")
        return self.qa_chain({"query": question})
