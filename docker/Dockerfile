FROM python:3.10.8-slim

COPY *.whl /tmp/
RUN pip3 install --no-cache-dir /tmp/*.whl && \
    rm /tmp/*.whl

ENTRYPOINT ["demo_ex"]