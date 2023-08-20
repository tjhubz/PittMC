# ---- Base ----
FROM python:3.11-slim-buster AS base
COPY webhook.py /PittMC/webhook.py
WORKDIR /PittMC

# ---- Dependencies ----
FROM base as dependencies
COPY requirements.txt /PittMC/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ---- Release ----
FROM dependencies AS release
CMD [ "python", "webhook.py" ]