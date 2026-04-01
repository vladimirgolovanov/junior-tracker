FROM python:3.13-slim

WORKDIR /app

RUN pip install poetry supervisor

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-root

COPY . .

COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 50081
CMD ["/entrypoint.sh"]
