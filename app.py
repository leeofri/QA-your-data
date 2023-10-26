from ingress.fileQa import csvQA
import sys

print("start")
app = csvQA(config={"file_path": "./data/Hebrew_reports.csv"})
print("start init embbeding")
app.init_embeddings()
if (sys.argv[0] == "load"):
    print("start load_docs_to_vec")
    app.load_docs_to_vec()

print("start answer_question")
print(app.answer_question("אירועים בשער צפון איזה היו?"))
