FROM python:3

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY . /app
COPY main.py /app
COPY /pywikibot/user-config.py /root/.pywikibot/user-config.py
RUN touch ARQMathCode/__init__.py
ENTRYPOINT ["python", "main.py" ]