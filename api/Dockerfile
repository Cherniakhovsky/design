FROM python:3.7.3-stretch AS prod

WORKDIR /usr/src/api

COPY Pipfile Pipfile.lock ./

RUN pip install pipenv

RUN pipenv install --deploy --system

COPY . /usr/src/api

CMD ["python", "./app.py"]

FROM prod AS dev

RUN pipenv install --dev --system

WORKDIR /usr/src

CMD ["adev", "runserver", "--app-factory", "make_app", "api/app.py"]
