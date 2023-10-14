FROM sbtscala/scala-sbt:eclipse-temurin-jammy-17.0.8.1_1_1.9.6_2.12.18
RUN apt-get update && apt-get install -y python3 graphviz

RUN mkdir /out
WORKDIR /app
COPY main.py .
COPY geyser ./geyser

ENTRYPOINT [ "python3", "main.py" ]
