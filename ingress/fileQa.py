import json
import os
import re
import pandas as pd
import asyncio
from langchain.docstore.document import Document
from langchain.document_loaders import CSVLoader
from langchain.text_splitter import CharacterTextSplitter, TokenTextSplitter, MarkdownTextSplitter, RecursiveCharacterTextSplitter, Language
from langchain.prompts import PromptTemplate
from langchain.vectorstores import Redis
from dotenv import load_dotenv
from ingress.utiles import Translate
from langchain.llms import LlamaCpp, OpenAIChat
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.schema import (
    AIMessage,
    BaseMessage
)
from redisvl.index import SearchIndex
from redisvl.query import VectorQuery
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
import sentence_transformers
from redisvl.vectorize.text import HFTextVectorizer
debug = True

load_dotenv()

from langchain.chains import RetrievalQA

redis_collection = os.environ.get("REDIS_COLLECTION", "reports")

class csvQA:
    def __init__(self,config:dict = {}):
        self.config = config
        self.embedding = None
        self.vectordb = None
        self.llm = None
        self.qa = None
        self.translator = None
        self.index = None

    def download_embedding_module(self):
        # self.embedding = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        # print("embdding cache folder:",self.embedding.cache_folder)
        self.embedding = HFTextVectorizer(model="sentence-transformers/all-MiniLM-L6-v2")
        print("embdding loaded")

    def init_transalte(self):
        self.translator = Translate()

    def init_embeddings(self) -> None:
        # OPensource local emmbeding
        # create the open-source embedding function
        if self.embedding is None:
            self.download_embedding_module()
        # self.vectordb = Redis(index_name=redis_collection,embedding=self.embedding,redis_url=os.environ.get("REDIS_URL", "redis://localhost:6379"))
        self.init_transalte()

    def init_llm(self) -> None:

        self.llm = OpenAIChat(
            model_name='mistral-7B-v0.1',
            temperature=0.65,
            max_tokens=1024,
            top_p=1,
            n_batch=100,
            n_ctx=1024,
            n_threads=32,
            # openai_api_base=os.environ.get("VLLM_API_BASE","http://localhost:8000/v1"),
            # callback_manager=callback_manager,
            verbose=True
        )
        

    def get_chat(self):
        template = """
        you are army command and control summerize reports system, please answer the question
        following this rules when generating and answer:
        - Use only the data from the reports log
        - the answer contain event from reports log in chronological order
        - mention the Sender and Destination of the source events in the answer
        =========
        reports log : {context}
        Quesion of the user : {question}
        =========
       answer: 
        """

        PROMPT = PromptTemplate(
            template=template, input_variables=["context", "question"]
        )

        # chain_type_kwargs = {"prompt": PROMPT}
        retriever = self.vectordb.as_retriever(
            search_kwargs={"k":6},
            )

        memory = ConversationBufferMemory(memory_key="chat_history", output_key='answer',input_key='question',return_messages=True)

        return ConversationalRetrievalChain.from_llm( 
            self.llm,  
            retriever, 
            memory=memory,
            verbose=True,
            return_source_documents=True,
            )
        
    def load_docs_to_vec(self,force_reload:bool= False) -> None:
        """
        creates vector db for the embeddings and persists them or loads a vector db from the persist directory
        """

        file_path = self.config.get("file_path",None)
        # vector_db_host = self.config.get("vector_db_host","localhost")
        #documents = CSVLoader(file_path=file_path,).load()
        df = pd.read_csv(file_path)
        print("Loaded {0} documents".format(len(df)))

        # if not documents or all(isinstance(item, list) and not item for item in documents):
        #     print("No new documents found")
        #     return     
             
        ##TODO: Validate if self.embedding is not None
        print("Creating vector db")
        records = []
        for _, record in df.iterrows():
            i=1
            new_record = record.copy(deep=True)
            en_text = self.translator.translate_he_to_en(new_record["Message"])
            en_vector = self.embedding.embed(en_text, as_buffer=True)
            new_record["en_text"]=en_text
            new_record["en_vector"] = en_vector
            en_location = self.translator.translate_he_to_en(new_record["Location"])
            en_loaction_vector = self.embedding.embed(en_location, as_buffer=True)
            new_record["en_location"] = en_location
            new_record["en_loaction_vector"] = bytes(en_loaction_vector)
            records.append(new_record)

        chunked_data = pd.DataFrame(records)
        # Adding a running number column using range
        chunked_data['RunningNumber'] = range(1, len(chunked_data) + 1)

        self.index = SearchIndex.from_yaml("./data/hebrew_reports_schema.yaml")
        self.index.connect("redis://localhost:6379")
        self.index.create(overwrite=True)
        self.index.load(chunked_data.to_dict(orient="records"))
        i=1
        # map over all the docs and translate them
        # translated_docs = []
        # for doc in documents:
        #     en_text = self.translator.translate_he_to_en(doc.page_content)
        #     newDoc = Document(page_content=en_text,metadata=doc.metadata)
        #     newDoc.metadata["he_text"] = doc.page_content
        #     # newDoc.metadata["content_heb_embed"] =
        #     translated_docs.append(newDoc)
        #
        # self.vectordb.from_documents(documents=translated_docs,embedding=self.embedding,index_name=redis_collection)

    def answer_question(self,question:str) ->str:
        """
        Answer the question
        """
        en_question = self.translator.translate_he_to_en(question)
        print(en_question)

        print("collection:" , self.vectordb._collection.count() )
        results = self.vectordb.similarity_search(en_question)

        return results
    
    # def retreival_qa_chain(self,question,history) -> None:
    #     en_question = self.translator.translate_he_to_en(question)
    #     res = self.chain({"query":en_question,history:history})
    #     print("en:",res["result"])
    #     he_result = self.translator.translate_en_to_he(res["result"])
    #     print("he:",he_result)
    #     return he_result
    
    def chat_with_history(self,meg:str) -> AIMessage:
        """
        Answer the question in a chat with history
        """
        print({"question": meg})
        he_query = meg
        en_query = self.translator.translate_he_to_en(he_query)

        print({"en question": en_query})

        result = self.chat({"question": en_query})

        print("en:",result)

        he_result = self.translator.translate_en_to_he(result["answer"])

        return AIMessage(content=he_result,source_documents=result["source_documents"])
