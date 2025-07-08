# k8s-config-secret-lab/Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app.py .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
