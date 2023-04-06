FROM nginx/unit:1.29.1-python3.11

WORKDIR /app

# Copy source code
COPY ./src ./src
COPY ./static ./static
COPY ./README.md ./pyproject.toml ./
COPY ./config.json /docker-entrypoint.d/

# Install dependencies
RUN mkdir -m 777 /app/artifacts
RUN python -m pip install tox==3.28 poetry==1.4.2 && \
    poetry config virtualenvs.create false && \
    poetry install --without dev,test
