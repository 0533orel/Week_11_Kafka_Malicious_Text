FROM python:3.11-slim
WORKDIR /app
COPY services/preprocessor/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY common /app/common
COPY services/preprocessor /app
CMD ["python", "app.py"]
