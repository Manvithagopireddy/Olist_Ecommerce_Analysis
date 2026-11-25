FROM python:3.12-slim
WORKDIR /app
COPY requirements-platform.txt .
RUN pip install --no-cache-dir -r requirements-platform.txt
COPY analytics_core.py pipeline.py dashboard_app.py ./
RUN useradd -m appuser && mkdir data && chown appuser data
USER appuser
EXPOSE 8501
CMD ["streamlit", "run", "dashboard_app.py", "--server.address=0.0.0.0"]
