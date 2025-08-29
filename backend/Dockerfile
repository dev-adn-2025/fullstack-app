FROM python:3.11-slim
WORKDIR /workspace
COPY pyproject.toml .
RUN pip install poetry && poetry install --no-root
COPY app/ app/
CMD ["poetry", "run", "flask", "--app", "app.main", "run", "--host=0.0.0.0", "--port=8000"]
