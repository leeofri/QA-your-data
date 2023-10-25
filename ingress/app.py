import json
import os
import re
from typing import Iterable, List
from langchain.docstore.document import Document
from langchain.document_loaders import CSVLoader
from langchain.text_splitter import CharacterTextSplitter, TokenTextSplitter, MarkdownTextSplitter, RecursiveCharacterTextSplitter, Language
from langchain.prompts import PromptTemplate
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv

from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings


load_dotenv()

from langchain.vectorstores import  Milvus
from langchain.chains import RetrievalQA

print("debug:", os.getenv("OPENAI_API_EMBEDDING_DEPLOYMENT_NAME"))

class FileQA:
    def __init__(self,config:dict = {}):
        self.config = config
        self.embedding = None
        self.vectordb = None
        self.llm = None
        self.qa = None
        self.retriever = None

    def init_embeddings(self) -> None:
        # OPensource local emmbeding
        # create the open-source embedding function
        self.embedding =  SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vectordb = Chroma(embedding_function=self.embedding)

    def init_models(self) -> None:
        # OpenAI GPT 3.5 API
        self.llm = ChatOpenAI(temperature=0.)
        
    def load_docs_to_vec(self,force_reload:bool= False) -> None:
        """
        creates vector db for the embeddings and persists them or loads a vector db from the persist directory
        """

        file_path = self.config.get("file_path",None)
        # vector_db_host = self.config.get("vector_db_host","localhost")
        documents = CSVLoader.load(
            file_path=file_path,
            # space_key=os.getenv("CONFLUENCE_SPACE_KEY"
        )
            
        print("Loaded {0} documents".format(len(documents)))

        # if not documents or all(isinstance(item, list) and not item for item in documents):
        #     print("No new documents found")
        #     return     
             
        ##TODO: Validate if self.embedding is not None
        print("Creating vector db")

        self.vectordb.from_documents(documents=documents,embedding=self.embedding,persist_directory='./data')

        # Append to each document new prop called pk and contain the id of the document
        # for doc in documents:
        #     doc.metadata["pk"] = doc.metadata["id"]

        # self.vectordb.from_documents(documents=texts)
    def retreival_qa_chain(self):
        """
        Creates retrieval qa chain using vectordb as retrivar and LLM to complete the prompt
        """
        ##TODO: Use custom prompt
        self.retriever = self.vectordb.as_retriever(search_kwargs={"k":4})
        self.qa = RetrievalQA.from_chain_type(llm=self.llm, chain_type="stuff",retriever=self.retriever)

    def answer_question(self,question:str) ->str:
        """
        Answer the question
        """
        answer = self.qa.run(query=question,verbose=True)
        return answer
    
    