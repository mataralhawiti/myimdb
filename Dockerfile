# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-slim-buster

LABEL Name=gomovies

EXPOSE 5000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

# Install pip requirements
ADD requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
ADD . /app

# Switching to a non-root user, please refer to https://aka.ms/vscode-docker-python-user-rights
RUN useradd appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
#To give Python Web Developers a great starting point, we chose to use Gunicorn as the default web server. 
#Since it is referenced in the default Dockerfile, it is included as a dependency in the requirements.txt file.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
