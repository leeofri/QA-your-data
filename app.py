from ingress.fileQa import csvQA

print("start")
app = csvQA(config={"file_path": "data/test_data.csv"})
print("start init embbeding")
app.init_embeddings()
print("start  load_docs_to_vec")
app.load_docs_to_vec()
print("start answer_question")
print(app.answer_question("אירועים בשער צפון איזה היו?"))
