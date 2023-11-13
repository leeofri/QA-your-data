import resource

from dotenv import load_dotenv

from langchain.callbacks import AimCallbackHandler

from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage


import chainlit as cl
from ingress.utiles import Translate

from ingress.fileQa import csvQA
import sys

app = csvQA(config={"file_path": "./data/Hebrew_reports.csv"})


@cl.on_chat_start
async def on_chat_start():
    print("start init embbeding")
    app.init_embeddings()
    print("start init LLM models ")
    app.init_llm()
    # print("Init redis with reports")
    # app.load_docs_to_vec()

    print(app.translator.translate_he_to_en("בדיקה אשש"))
    print(app.translator.translate_en_to_he("test broo"))

    cl.user_session.set("chain", app.get_chat())


@cl.on_message
async def on_message(message: cl.Message):
    chain = cl.user_session.get("chain")  # type: LLMChain
    en_query = app.translator.translate_he_to_en(message.content)

    # Init the callback
    aim_callback = AimCallbackHandler(
        repo=".",
        experiment_name="v0.0.1",
    )

    res = await cl.make_async(chain)(
        en_query,
        callbacks=[cl.LangchainCallbackHandler(), aim_callback],
    )

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
    aim_callback.flush_tracker(langchain_asset=chain, reset=False, finish=True)

    # run = lambda question,callbacks : chain({"question":question})

    # res = await cl.make_async(run)(
    #    question=en_query, callbacks=[cl.LangchainCallbackHandler()]
    # )

    # res["answer"] = translate.translate_en_to_he(res["answer"])

    # await cl.Message(content=res).send()
