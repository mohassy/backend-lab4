# Use Python 3.12 Alpine base image
FROM python:3.12-alpine

# Set working directory
WORKDIR /code

# Copy requirements.txt to working directory
COPY requirements.txt /code/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the entire app directory to the working directory
COPY ./app /code/app

# Set the working directory to /code/app
WORKDIR /code/app

# Command to run the FastAPI application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
