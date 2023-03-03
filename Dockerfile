# docker build -t weather-server:2023-03-03 .
# docker tag weather-server:2023-03-03 weather-server
# docker run -d --privileged --restart unless-stopped -p 2020:2020/udp --name weather-server weather-server

#
# temp stage
#
FROM python:3.11-buster as build
ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1
WORKDIR /src
COPY requirements.txt ./
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

#
# final stage
#
FROM python:3.11-slim
LABEL maintainer="Alvaro Figueiredo <alvaro.af@gmail.com>"
ENV PYTHONUNBUFFERED 1
WORKDIR /app
EXPOSE 2020/udp
COPY --from=build /app/wheels /wheels
RUN pip install --no-cache-dir /wheels/* \
    && rm -rf /wheels
COPY server.py ./

CMD ["python", "./server.py"]
