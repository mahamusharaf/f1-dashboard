FROM python:3.13-slim

# Hugging Face Spaces require running as non-root user
RUN useradd -m -u 1000 user

USER user
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Copy requirements first to leverage Docker cache
COPY --chown=user backend/requirements.txt $HOME/app/

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of the backend code
COPY --chown=user backend/ $HOME/app/

# Hugging Face Spaces needs to be able to write to the cache directory
RUN mkdir -p f1_cache && chmod -R 777 f1_cache

# Expose the default HF Spaces port
EXPOSE 7860

# Run the FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
