FROM python:3.12-alpine

WORKDIR /app

RUN apk add --no-cache gcc musl-dev python3-dev linux-headers net-tools

COPY requirements.txt .

RUN pip install --upgrade pip && pip install --upgrade -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]