docker build -t hacks-backend .
docker run --rm -p 8000:8000 --entrypoint python --env-file .env hacks-backend main.py

Push works for Sid changes, Dhruv starts working
