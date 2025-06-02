# core-service/Dockerfile
FROM python:3.12-slim

# 1) دایرکتوری کاری داخل کانتینر
WORKDIR /app

# 2) نصب وابستگی‌ها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) کد برنامه
COPY app ./app
COPY main.py .

# 4) فرمان اجرا
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
