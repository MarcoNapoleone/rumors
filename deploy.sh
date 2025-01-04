docker build -t rumors:latest .

docker tag rumors:latest marconapo/rumors:latest

docker push marconapo/rumors:latest
