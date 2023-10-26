from ingress.fileQa import csvQA
import sys

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
print(app.retreival_qa_chain("אירועים בשער צפון איזה היו?"))
