FROM python:3.11.11-slim-bookworm

LABEL org.opencontainers.image.source="https://github.com/dantwoashim/Project_Parva"
LABEL org.opencontainers.image.description="Read-only MCP server for Project Parva Nepali temporal tools"
LABEL org.opencontainers.image.licenses="AGPL-3.0-or-later"
LABEL io.modelcontextprotocol.server.name="io.github.dantwoashim/project-parva"

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN python -m pip install --no-cache-dir . \
    && useradd --create-home --shell /usr/sbin/nologin parva

USER parva

ENTRYPOINT ["parva-mcp-server"]
CMD ["--stdio"]
