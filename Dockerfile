FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the built wheel file to the container
COPY dist/*.whl /app/

RUN mkdir /app/static
COPY static /app/static/

# Install Poetry for dependency management
RUN pip install --no-cache-dir poetry

# Install the wheel package
RUN pip install --no-cache-dir /app/*.whl

# Expose the application port
EXPOSE 8000

# Command to run the FastAPI application
CMD ["python", "-m", "codeshieldapp.main"]
