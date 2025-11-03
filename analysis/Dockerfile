FROM python:3.12-slim

RUN pip install uv

WORKDIR /app

COPY pyproject.toml uv.lock* ./

RUN uv sync --no-dev --frozen

COPY . .

CMD ["uv", "run", "python", "main.py"]