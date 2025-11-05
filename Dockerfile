# Base image
FROM python:3.10

# Set working directory
WORKDIR /usr/src/backend

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy all application files
COPY . .

# Expose application port
EXPOSE 8000

# Define default command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]