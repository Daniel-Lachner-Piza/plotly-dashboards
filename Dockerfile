# 1. Base Image
FROM python:3.14.0rc1-alpine3.22

# 2. Metadata
LABEL author="Daniel Lachner-Piza"
LABEL version="1.0"
LABEL description="Dockerfile for a Dashboard Application"

# 3. System Setup
RUN apt-get update && apt-get install -y \
build-essential \
&& rm -rf /var/lib/apt/lists/*

RUN pip install -U pip

# 4. Application Setup
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# 5. Application Code
COPY src/ ./src/
COPY Stage_Spike_Occurrence_Rate/ ./Stage_Spike_Occurrence_Rate/

# 6. Runtime Configuration
EXPOSE 8050

ENTRYPOINT [ "gunicorn", "--bind", "0.0.0.0:8050", "src.persyst_dashboard:app" ]
#ENTRYPOINT ["/bin/sh"]