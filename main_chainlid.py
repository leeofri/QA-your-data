import resource

from dotenv import load_dotenv
import os
import json

from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    SystemMessage,
    HumanMessage,
    AIMessage
)


from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig

import chainlit as cl
from ingress.utiles import Translate

from ingress.fileQa import csvQA
import sys

@cl.on_chat_start
async def on_chat_start():
    app = csvQA(config={"file_path": "./data/Hebrew_reports.csv"})
    print("start init embbeding")
    app.init_embeddings()
    print("start init LLM models ")
    app.init_llm()
    print("Init redis with reports")
    app.load_docs_to_vec()

    print(app.translator.translate_he_to_en("בדיקה אשש"))
    print(app.translator.translate_en_to_he("test broo"))
   
    cl.user_session.set("chain", app.chat)
    cl.user_session.set("app", app)


@cl.on_message
async def on_message(message: cl.Message):
    chain = cl.user_session.get("chain")  # type: LLMChain
    app = cl.user_session.get("app") 
    
    en_query = app.translator.translate_he_to_en(message.content)

    cb = cl.AsyncLangchainCallbackHandler()

    res = await chain({"question"=en_query, "callbacks"=[cb]})
    answer = app.translator.translate_en_to_he(res["answer"])
    source_documents = res["source_documents"]  # type: List[Document]

    text_elements = []  # type: List[cl.Text]

    if source_documents:
        for source_idx, source_doc in enumerate(source_documents):
            source_name = f"source_{source_idx}"
            # Create the text element referenced in the message
            text_elements.append(
                cl.Text(content=source_doc.page_content, name=source_name)
            )
        source_names = [text_el.name for text_el in text_elements]

        if source_names:
            answer += f"\nדיווחים: {', '.join(source_names)}"
        else:
            answer += "\nלא נמצאו דיווחים תואמים"

    await cl.Message(content=answer, elements=text_elements).send()







    # run = lambda question,callbacks : chain({"question":question})

    # res = await cl.make_async(run)(
    #    question=en_query, callbacks=[cl.LangchainCallbackHandler()]
    # )

    # res["answer"] = translate.translate_en_to_he(res["answer"])

    # await cl.Message(content=res).send()

