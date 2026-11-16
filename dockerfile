# Start fra et færdigt image med Python 3.12 installeret
FROM python:3.12-slim

# Arbejdsmappen inde i containeren
WORKDIR /app

# Installer pakkerne først (så Docker kan genbruge dette trin, når kun koden ændrer sig)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiér resten af koden ind
COPY . .

# Containeren lytter på port 8000
EXPOSE 8000

# Start serveren, når containeren starter
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]