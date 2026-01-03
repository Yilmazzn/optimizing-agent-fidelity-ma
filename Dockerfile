FROM python:3.13
WORKDIR /app

# download deps
COPY pyproject.toml uv.lock ./
RUN pip install uv && \
    uv sync --frozen --no-dev --no-install-project
ENV PATH="/app/.venv/bin:$PATH"

# build proj
COPY .env ./ 
COPY src ./src
ENV PYTHONPATH="/app/src"

EXPOSE 9876
CMD ["python", "./src/main.py"]