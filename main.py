import resource

import streamlit as st
from dotenv import load_dotenv
import os

from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    SystemMessage,
    HumanMessage,
    AIMessage
)

from ingress.fileQa import csvQA
import sys

app = csvQA(config={"file_path": "./data/Hebrew_reports.csv"})

def init():
    # Load the OpenAI API key from the environment variable
    load_dotenv()
    print("start")
    
    print("start init embbeding")
    app.init_embeddings()
    print("start init LLM models ")
    app.init_llm()
    print("start answer_question")
    if (len(sys.argv) >=2 and sys.argv[1] == "load"):
        print("start load_docs_to_vec")
        app.load_docs_to_vec()
        

    # setup streamlit page
    st.set_page_config(
        page_title="ReportAI",
        page_icon="🤖"
    )


def main():
    init()

    # initialize message history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            SystemMessage(content="You are a helpful assistant.")
        ]

    st.header("ReportAI 🤖")

    # sidebar with user input
    with st.sidebar:
        user_input = st.text_input("Your message: ", key="user_input")

        # handle user input
        if user_input:
            print("user_input",user_input)
            st.session_state.messages.append(HumanMessage(content=user_input))
            with st.spinner("Thinking..."):
                response = app.chat_with_history(st.session_state.messages[-1].content)
            st.session_state.messages.append(
                AIMessage(content=response.content))

    # display message history
    messages = st.session_state.get('messages', [])
    for i, msg in enumerate(messages[1:]):
        if i % 2 == 0:
            st.chat_message("user").write(msg.content)
        else:
            st.chat_message("assistant").write(msg.content)


if __name__ == '__main__':
    main()