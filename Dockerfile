FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
EXPOSE 8501

CMD streamlit run dashboard.py --server.address=0.0.0.0 & pyhon app.py

