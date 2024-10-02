FROM python:3.9-slim
WORKDIR /app
RUN pip install gunicorn==20.1.0
COPY blogicum/requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY blogicum .
CMD ["gunicorn", "--bind", "0:8000", "blogicum.wsgi" ]
#CMD ["python", "manage.py", "runserver", "0:8000" ]