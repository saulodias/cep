FROM postgres:17-alpine

# Set environment variables
ENV POSTGRES_DB=cep_database
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres

# Install required packages
RUN apk add --no-cache tar

# Copy the address_pt.syn file to PostgreSQL's tsearch_data directory
COPY address_pt.syn /usr/share/postgresql/tsearch_data/address_pt.syn

# Set permissions for the address_pt.syn file
RUN chown postgres:postgres /usr/share/postgresql/tsearch_data/address_pt.syn && \
    chmod 644 /usr/share/postgresql/tsearch_data/address_pt.syn

# Copy the SQL files and data
COPY sql/ /docker-entrypoint-initdb.d/

# Create a script to run SQL files in order
RUN echo '#!/bin/bash' > /docker-entrypoint-initdb.d/00_run_sql.sh && \
    echo 'psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL' >> /docker-entrypoint-initdb.d/00_run_sql.sh && \
    echo '    \i /docker-entrypoint-initdb.d/create_tables.sql' >> /docker-entrypoint-initdb.d/00_run_sql.sh && \
    echo '    \i /docker-entrypoint-initdb.d/setup_config.sql' >> /docker-entrypoint-initdb.d/00_run_sql.sh && \
    echo '    \i /docker-entrypoint-initdb.d/setup_normalization.sql' >> /docker-entrypoint-initdb.d/00_run_sql.sh && \
    echo '    \i /docker-entrypoint-initdb.d/setup_search_vectors.sql' >> /docker-entrypoint-initdb.d/00_run_sql.sh && \
    echo 'EOSQL' >> /docker-entrypoint-initdb.d/00_run_sql.sh && \
    chmod +x /docker-entrypoint-initdb.d/00_run_sql.sh
