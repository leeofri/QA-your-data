# QA-your-data

### install
```
python3 -m venv he_qa
source he_qa/bin/activate
pip install -r requirements.txt
```

## Download moodel
usinng GPT4all:

- downlad https://gpt4all.io/index.html
- insntall
- downlad from the UI,  mistral-7B-Instruct-v0.1
- change the modle path in code ->  
```
#fileQa.py
model_path="/Users/admin/Library/Application Support/nomic.ai/GPT4All/mistral-7b-instruct-v0.1.Q4_0.gguf"
```

mistralai/Mistral-7B-Instruct-v0.1
```
wget https://files.mistral-7b-v0-1.mistral.ai/mistral-7B-Instruct-v0.1.tar
tar -xf mistral-7B-v0.1.tar
```


### run app.py - each run will take all Hebrew_reports.csv transalte and embbed
```
python3 app.py load # for load data and preform sematic search
python3 app.py just sematic search on persist data in /data
```

## run UI - 
```
streamlit run main.py --logger.level debug
```


## eamples
סכם את האירועים בבסיס בברמינגטון
תאר לי את החשוד
מי שלח אותו לבסיס