# -------- BUILDER STAGE --------
FROM python:3.13-bookworm AS builder

WORKDIR /work

# Set up Python virtual environment
RUN python -m venv /opt/idems/venv
ENV PATH=/opt/idems/venv/bin:${PATH}
ENV PIP_NO_CACHE_DIR=1
COPY requirements.txt .
RUN pip install --upgrade -r requirements.txt


# -------- PROD STAGE --------
FROM python:3.13-slim-bookworm AS prod
WORKDIR /app

ENV PATH=/opt/idems/venv/bin:${PATH}
ENV PIP_NO_CACHE_DIR=1
ENV UVICORN_HOST=0.0.0.0
ENV UVICORN_PORT=8000

# Copy Python venv from builder
COPY --from=builder /opt/idems/venv /opt/idems/venv

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && chown -R appuser:appuser /app
USER appuser

# Copy app source
COPY --chown=appuser:appuser app app
COPY --chown=appuser:appuser entrypoint.sh .
RUN chmod +x entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "app.main:app"]