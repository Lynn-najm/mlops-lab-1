FROM python:3.11-slim

WORKDIR /app
RUN pip install --no-cache-dir "streamlit==1.39.0" requests

COPY app.py .

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
