FROM python:3.11-alpine

COPY ./pyproject.toml /app/pyproject.toml
COPY ./list_python_dependencies.py /app/
COPY ./action.yml /app/

RUN pip install /app/

CMD ["list_python_dependencies"]
