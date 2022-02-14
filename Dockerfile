FROM python:3.9

WORKDIR /home

COPY app ./app
COPY requeriments.txt requeriments.txt
COPY migrations ./migrations
COPY run.py .
RUN pip install -r requeriments.txt
ENV FLASK_APP=app/
CMD ["python", "run.py"]