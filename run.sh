#! /bin/bash
pip install -q -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000