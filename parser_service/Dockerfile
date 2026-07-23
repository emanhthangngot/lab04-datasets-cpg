FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Source is mounted by docker-compose for fast lab iteration.
CMD ["python", "-m", "parser_service.main", "--repo", "data/datasets", "--mode", "full"]
