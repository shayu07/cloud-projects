FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY project1_redundancy/ ./project1/
COPY project2_chatbot/ ./project2/
EXPOSE 5001 5002
CMD ["sh", "-c", "cd /app/project1 && gunicorn -b 0.0.0.0:5001 app:app --daemon && cd /app/project2 && gunicorn -b 0.0.0.0:5002 app:app"]
