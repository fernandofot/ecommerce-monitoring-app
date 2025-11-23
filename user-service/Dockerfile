# user-service/Dockerfile
# --- Stage 1: Build the application ---
FROM maven:3.8.5-openjdk-17 AS build

WORKDIR /app

COPY pom.xml .
RUN mvn dependency:go-offline

COPY src ./src
RUN mvn clean package -DskipTests

# --- Stage 2: Runtime image ---
# Use Eclipse Temurin JRE 17 (Debian-based, multi-arch)
FROM eclipse-temurin:17-jre

# Install netcat (Debian/Ubuntu use apt-get)
RUN apt-get update \
    && apt-get install -y --no-install-recommends netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8080

COPY --from=build /app/target/*.jar /user-service.jar

ENTRYPOINT ["java", "-jar", "/user-service.jar"]