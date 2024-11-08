FROM python:3.10-slim

WORKDIR /app

# Update SSL libraries and other dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    openssl \
    gcc \
    g++ \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies with retries and alternative PyPI mirror
RUN pip install --no-cache-dir --retries=5 --index-url https://pypi.org/simple/ \
    pandas \
    networkx \
    openai==0.28 \
    python-dotenv \
    tabulate \
    PyPDF2 \
    scikit-learn \
    spacy \
    faiss-cpu \
    torch \
    transformers 


# Download spacy language model
RUN python -m spacy download en_core_web_sm

COPY . .

ENV DB_PATH="/app/data/chinook_database_master.sqlite"

CMD ["python", "src/main.py"]
