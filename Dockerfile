# FIX: Updated Python version to a valid and commonly available slim image tag
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# FIX: Copying specific directories to reduce image size and ensure correct module resolution
# Instead of `COPY . .`, which is broad, let's copy only what's needed.
# This assumes your 'src' folder contains app.py, services/, config.py etc.
COPY src/ ./src/
COPY mocks/ ./mocks/
COPY data/ ./data/
# Copy any other top-level files needed at runtime, e.g.,
# COPY README.md . 
# COPY .env.example . # if you use .env files inside the container

EXPOSE 8000

# FIX: Corrected the CMD to point to the app inside the 'src' package
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]

