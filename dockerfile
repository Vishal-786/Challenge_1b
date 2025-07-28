FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Default command (override with --input, --pdf_dir, --output)
CMD ["python", "main.py"]