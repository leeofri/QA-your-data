from ingress.fileQa import csvQA
import sys
import csv
import datetime

print("start")
app = csvQA(config={"file_path": "./QA-your-data/data/Hebrew_reports.csv"})
print("start init embbeding")
app.init_embeddings()
# if (sys.argv[1] == "load"):
print("start load_docs_to_vec")
app.load_docs_to_vec()

print("start answer_question")
answer = app.answer_question("מי הלך לגדר המזרחית?")

# save answer to csv with timestamp in the name
filename = "answer_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".csv"
with open(filename, mode='w') as file:
    writer = csv.writer(file)
    writer.writerow(["Sender", "Recipient","Time", "Message"])  # header
    for i,element in enumerate(answer):
        parts = answer[i].metadata['he_text'].split('\n')
        sender = parts[0]
        recipient = parts[1]
        time = parts[2]
        message = parts[3]
        writer.writerow([sender, recipient, time, message])

print(answer)
