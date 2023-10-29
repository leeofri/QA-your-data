from ingress.fileQa import csvQA
import sys
import csv
import datetime

from bidi.algorithm import get_display # for correct display of Hebrew

print("start")
app = csvQA(config={"file_path": "./data/Hebrew_reports.csv"})


print("start init embbeding")
app.init_embeddings()
if (len(sys.argv) >=2 and sys.argv[1] == "load"):
    print("start load_docs_to_vec")
    app.load_docs_to_vec()

print("start init LLM models ")
app.init_llm()

print("start answer_question")
import sys

question = input("Enter your question: ")
history = ''

chain = app.retreival_qa_chain(question, history=history)
print(get_display(chain))

history = f'{question}\n{chain}\n'

while True:
    question = input("Enter your question: ")
    chain = app.retreival_qa_chain(question, history=history)
    print(get_display(chain))
    history += f'{question}\n{chain}\n'

    if question.lower() == "stop" or question.lower() == "exit":
        break
