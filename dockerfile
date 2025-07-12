FROM python:3.11-slim
WORKDIR /wms
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "gui.py", "--server.port=8501", "--server.address=0.0.0.0"]
