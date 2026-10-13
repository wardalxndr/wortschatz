install:
	pip install -r requirements.txt

ingest:
	python ingest/build_index.py

eval:
	python eval/evaluate.py

app:
	streamlit run app/app.py

test:
	pytest -q
