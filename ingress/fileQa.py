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
from langchain.llms import LlamaCpp
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


class csvQA:
    def __init__(self,config:dict = {}):
        self.config = config
        self.embedding = None
        self.vectordb = None
        self.llm = None
        self.qa = None
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

    def init_llm(self) -> None:
        self.llm = LlamaCpp(
            model_path="/Users/admin/Library/Application Support/nomic.ai/GPT4All/mistral-7b-instruct-v0.1.Q4_0.gguf",
            temperature=0.5,
            max_tokens=512,
            top_p=1,
            n_batch=1,
            n_ctx=1024,
            # callback_manager=callback_manager,
            verbose=True
            )
        
        template = """
        you are summerize events system, please answer the question
        following this rules when generating and answer:
        - Always prioritize the context for question ansering 
        - Make it short and clear
        =========
        context : {context}
        Quesion of the user : {question}
        =========
       answer: 
        """

        PROMPT = PromptTemplate(
            template=template, input_variables=["context", "question"]
        )

        chain_type_kwargs = {"prompt": PROMPT}
        retriever = self.vectordb.as_retriever(search_kwargs={"k":3})

        self.chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs=chain_type_kwargs,
            verbose=True,
        )


        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        self.chat = ConversationalRetrievalChain.from_llm( 
            self.llm,  
            retriever, 
            memory=self.memory,
            verbose=True,
            )
        
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

    def answer_question(self,question:str) ->str:
        """
        Answer the question
        """
        en_question = self.translator.translate_he_to_en(question)
        print(en_question)

        print("collection:" , self.vectordb._collection.count() )
        results = self.vectordb.similarity_search(en_question)

        return results
    
    def retreival_qa_chain(self,question,history) -> None:
        en_question = self.translator.translate_he_to_en(question)
        res = self.chain({"query":en_question,history:history})
        print("en:",res["result"])
        he_result = self.translator.translate_en_to_he(res["result"])
        print("he:",he_result)
        return he_result
    
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

        return AIMessage(content=he_result)
        
    