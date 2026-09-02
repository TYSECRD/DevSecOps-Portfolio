FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN python -m pip uninstall -y pip

RUN useradd --create-home steeldoor

COPY app ./app

RUN chown -R steeldoor:steeldoor /app

USER steeldoor

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]