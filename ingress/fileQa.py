import json
import os
import re
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

from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
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

    def download_embedding_module(self):
        self.embedding =  SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        print("embdding cache folder:",self.embedding.cache_folder)

    def init_transalte(self):
        self.translator = Translate()

    def init_embeddings(self) -> None:
        # OPensource local emmbeding
        # create the open-source embedding function
        if self.embedding is None:
            self.download_embedding_module()
        self.vectordb = Redis(index_name=redis_collection,embedding=self.embedding,redis_url=os.environ.get("REDIS_URL", "redis://localhost:6379"))
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
            openai_api_base=os.environ.get("VLLM_API_BASE","http://localhost:8000/v1"),
            # callback_manager=callback_manager,
            verbose=True
        )
        
        
        # LlamaCpp(
        #     model_path=os.environ.get("MODEL_PATH", "/Users/admin/Library/Application Support/nomic.ai/GPT4All/mistral-7b-instruct-v0.1.Q4_0.gguf"),
        #     temperature=0.8,
        #     max_tokens=1024,
        #     top_p=1,
        #     n_batch=100,
        #     n_ctx=1024,
        #     n_threads=32,
        #     # callback_manager=callback_manager,
        #     verbose=True
        #     )
        
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

        self.memory = ConversationBufferMemory(memory_key="chat_history", output_key='answer',input_key='question',return_messages=True)

        self.chat = ConversationalRetrievalChain.from_llm( 
            self.llm,  
            retriever, 
            memory=self.memory,
            verbose=True,
            return_source_documents=True,
            callbacks=[]
            )
        
    def load_docs_to_vec(self,force_reload:bool= False) -> None:
        """
        creates vector db for the embeddings and persists them or loads a vector db from the persist directory
        """

        file_path = self.config.get("file_path",None)
        # vector_db_host = self.config.get("vector_db_host","localhost")
        documents = CSVLoader(file_path=file_path,).load()
            
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
            
        self.vectordb.from_documents(documents=translated_docs,embedding=self.embedding,index_name=redis_collection)

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
