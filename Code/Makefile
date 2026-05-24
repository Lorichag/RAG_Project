setup:
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt

run-api:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

lint:
	python -m py_compile app/**/*.py

test:
	python -m pytest

format:
	python -m black app scripts dags
