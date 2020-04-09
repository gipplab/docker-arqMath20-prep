FROM python:3

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY . /app
COPY main.py /app
RUN touch ARQMathCode/__init__.py
ENTRYPOINT ["python", "main.py" ]