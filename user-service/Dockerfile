# user-service/Dockerfile
# This Dockerfile uses a multi-stage build to create a small, efficient image.

# --- Stage 1: Build the application ---
# We use a Maven image to build our Java application. This stage contains all
# the tools needed to compile the code and build the .jar file.
FROM maven:3.8.5-openjdk-17 AS build

# Set the working directory inside the container.
WORKDIR /app

# Copy the project's dependency file (pom.xml) first.
# This helps Docker cache the dependencies, so if the pom.xml doesn't change,
# it won't re-download everything on every build.
COPY pom.xml .

# Download the project's dependencies.
RUN mvn dependency:go-offline

# Copy the rest of the application's source code.
COPY src ./src

# Build the Spring Boot application and package it into a single executable JAR.
RUN mvn clean package -DskipTests

# --- Stage 2: Create the final production image ---
# We switch to a much smaller, more secure OpenJDK image.
# This final image will only contain the Java Runtime Environment and our application.
FROM openjdk:17-slim

# This is the new, crucial step! We need to install the 'netcat' utility
# so that our health check can properly verify if the service is up.
RUN apt-get update && apt-get install -y netcat && rm -rf /var/lib/apt/lists/*

# Expose the port that our Spring Boot application will run on.
EXPOSE 8080

# Copy the built JAR file from the 'build' stage into our final image.
COPY --from=build /app/target/*.jar user-service.jar

# Define the command that will run when the container starts.
# This command executes our JAR file.
ENTRYPOINT ["java", "-jar", "/user-service.jar"]
