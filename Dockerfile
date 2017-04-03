FROM python:3.6

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
ENV PYTHONPATH $PYTHONPATH:/urs/src/app

ADD requirements.txt .
RUN pip install -r requirements.txt
ADD *.py /usr/src/app/

CMD ["python", "main.py"]