# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/engine/reference/builder/

ARG PYTHON_VERSION=3.11.5
FROM python:${PYTHON_VERSION}-slim as base

RUN apt-get update && apt-get install -y pkg-config libavcodec-dev libavdevice-dev \
    libavfilter-dev libavformat-dev libavutil-dev libswresample-dev libswscale-dev  && rm -rf /var/lib/apt/lists/*

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1


WORKDIR /app

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=1000 
RUN adduser \
    --disabled-password \
    --gecos "" \
    --uid "${UID}" \
    appuser

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install --no-cache-dir --upgrade -r requirements.txt

RUN mkdir upload_files && chown appuser upload_files

# Switch to the non-privileged user to run the application.
USER appuser

# Copy the source code into the container.
COPY --chown=user . .

# Expose the port that the application listens on.
EXPOSE 5000

# Run the application.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0" , "--reload", "--port", "5000"]
