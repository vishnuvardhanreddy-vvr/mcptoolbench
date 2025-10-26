# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements from root and install
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY app/ /app/

# Expose default Streamlit port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
