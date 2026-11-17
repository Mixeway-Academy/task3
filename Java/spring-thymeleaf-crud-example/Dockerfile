# ---- Build Stage ----
FROM maven:3.8.3-openjdk-11-slim AS build

WORKDIR /app

COPY src /app/src
COPY pom.xml /app

RUN mvn -B clean package

# ---- Deploy Stage ----
FROM eclipse-temurin:11-jdk

COPY --from=build /app/target/thymeleaf-0.0.1-SNAPSHOT.jar /app.jar

ENTRYPOINT ["java", "-jar", "/app.jar"]