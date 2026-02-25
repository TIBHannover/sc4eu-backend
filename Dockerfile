FROM python:3.14-trixie
LABEL maintainer="Vitalis Wiens <Vitalis.Wiens@tib.eu>"

WORKDIR /app

COPY requirements.txt /app

# Install requirements
RUN \
  pip install --upgrade pip && \
  pip install --no-cache -r requirements.txt && \
  rm -rf ~/.cache/

# Add the rest of the code to the app folder
COPY . /app

EXPOSE 5000
EXPOSE 5050

# Apply the migration to the database and run the application
CMD flask db upgrade && \
    python app.py & \
    python app_fastapi_factory.py