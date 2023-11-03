# Use Python image from Dockerhub as a parent image
FROM python:3.9-slim-buster

# Prevents Python from generating .pyc files in the container.
ENV PYTHONDONTWRITEBYTECODE=1
# Turns off buffering for easier container logging.
ENV PYTHONUNBUFFERED=1
# Force UTF8 encoding for funky characters.
ENV PYTHONIOENCODING=utf8

# Install MariaDB
RUN apt-get update -y && \
    apt-get install --no-install-recommends -y \
    build-essential \
    libmariadb-dev-compat \
    libmariadb-dev \
    python-mysqldb \
    git

# Set the working directory in the container
WORKDIR /app

# Copy the application code into the container at /app
COPY . /app

# Update pip and install the requirements.
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Command to run the application when the container starts
CMD ["python", "app.py"]