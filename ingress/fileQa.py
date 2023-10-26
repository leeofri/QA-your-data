import json
import os
import re
from typing import Iterable, List
from langchain.docstore.document import Document
from langchain.document_loaders import CSVLoader
from langchain.text_splitter import CharacterTextSplitter, TokenTextSplitter, MarkdownTextSplitter, RecursiveCharacterTextSplitter, Language
from langchain.prompts import PromptTemplate
from langchain.vectorstores import Chroma
from dotenv import load_dotenv
from ingress.utiles import Translate

from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings


load_dotenv()

from langchain.chains import RetrievalQA


class csvQA:
    def __init__(self,config:dict = {}):
        self.config = config
        self.embedding = None
        self.vectordb = None
        self.llm = None
        self.qa = None
        self.retriever = None
        self.translator = None

    def init_embeddings(self) -> None:
        # OPensource local emmbeding
        # create the open-source embedding function
        self.embedding =  SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vectordb = Chroma(embedding_function=self.embedding,persist_directory='./data')
        self.translator = Translate()

    # def init_models(self) -> None:
    #     # # OpenAI GPT 3.5 API
    #     self.llm = ChatOpenAI(temperature=0.)
        
    def load_docs_to_vec(self,force_reload:bool= False) -> None:
        """
        creates vector db for the embeddings and persists them or loads a vector db from the persist directory
        """

        file_path = self.config.get("file_path",None)
        # vector_db_host = self.config.get("vector_db_host","localhost")
        documents = CSVLoader(file_path=file_path).load()
            
        print("Loaded {0} documents".format(len(documents)))

        # if not documents or all(isinstance(item, list) and not item for item in documents):
        #     print("No new documents found")
        #     return     
             
        ##TODO: Validate if self.embedding is not None
        print("Creating vector db")

        # map over all the docs and translate them
        translated_docs = []
        for doc in documents:
            en_text = self.translator.translate_he_to_en(doc.page_content)
            newDoc = Document(page_content=en_text,metadata=doc.metadata)
            newDoc.metadata["he_text"] = doc.page_content
            translated_docs.append(newDoc)
            

        self.vectordb.from_documents(documents=translated_docs,embedding=self.embedding,persist_directory='./data')

        self.vectordb
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
        en_question = self.translator.translate_he_to_en(question)
        print(en_question)

        print("collection:" , self.vectordb._collection.count() )
        results = self.vectordb.similarity_search(en_question)

        map(lambda x: print(x.page_content),results)

        return results

    
