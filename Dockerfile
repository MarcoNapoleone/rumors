# Usa un'immagine di base con Python
FROM python:3.12
# Imposta la directory di lavoro
WORKDIR /app

# Copia il file requirements.txt e installa le dipendenze
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copia il resto del codice dell'app
COPY . .

# Espone la porta su cui l'app Flask è in esecuzione
EXPOSE 5000

# Comando per avviare l'app
CMD ["python", "run.py"]
