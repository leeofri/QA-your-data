from ingress.fileQa import csvQA
import sys
from ingress.utiles import Translate

print("start")
app = csvQA(config={"file_path": "./data/Hebrew_reports.csv"})


print("start init embbeding")
app.download_embedding_module()

print("check translate module")
app.init_transalte()
app.translator.translate_he_to_en("בדיקה אשש")
app.translator.translate_en_to_he("test broo")
# print(translate.translate_he_to_en("בדיקה אשש"))
# print(translate.translate_en_to_he("test broo"))
# print(Translate().translate_he_to_en("בדיקה אשש"))
# print(Translate().translate_en_to_he("I want to eat apple pie and drink hot tea"))


# if (len(sys.argv) >=2 and sys.argv[1] == "load"):
#     print("start load_docs_to_vec")
#     app.load_docs_to_vec()

# print("start init LLM models ")
# app.init_llm()

# print("start answer_question")
# print(app.retreival_qa_chain("אירועים בשער צפון איזה היו?"))
