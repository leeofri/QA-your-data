from ingress.fileQa import csvQA
import sys
from ingress.utiles import Translate

print("start")
app = csvQA(config={"file_path": "./data/Hebrew_reports.csv"})


print("start init embbeding")
app.init_embeddings()

print("check translate module")
app.init_transalte()
app.translator.translate_he_to_en("בדיקה אשש")
app.translator.translate_en_to_he("test broo")

if (len(sys.argv) >=2 and sys.argv[1] == "load"):
        print("start load_docs_to_vec")
        app.load_docs_to_vec()
        




