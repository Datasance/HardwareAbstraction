FROM python:3.9.21-alpine3.21

RUN apk add --no-cache \
    util-linux \
    pciutils \
    lshw \
    build-base \
    python3-dev && \
    pip install --no-cache-dir --upgrade pip pyserial autobahn RPi.GPIO && \
    apk del build-base python3-dev
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir pyserial autobahn RPi.GPIO

COPY . /src/
RUN cd /src;
LABEL org.opencontainers.image.description=HAL
LABEL org.opencontainers.image.source=https://github.com/datasance/hardwareabstraction
LABEL org.opencontainers.image.licenses=EPL2.0
CMD ["python3", "/src/hal_main.py"]