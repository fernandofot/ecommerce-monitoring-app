# Build Stage
# We'll use the .NET SDK image to build our application.
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build

# Set the working directory inside the container.
WORKDIR /app

# Copy the project file first and restore dependencies.
# This leverages Docker's layer caching to speed up subsequent builds.
# We are correcting the project file name from "OrderService.csproj" to "order-service.csproj"
COPY "order-service.csproj" ./
RUN dotnet restore "order-service.csproj"

# Copy the rest of the application code.
COPY . .

# Build the application for release.
RUN dotnet build "order-service.csproj" -c Release

# Publish the application, ready to be run.
RUN dotnet publish "order-service.csproj" -c Release -o /app/publish

# Final Stage
# We'll use a smaller, production-ready ASP.NET Core runtime image.
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS final

# Set the working directory.
WORKDIR /app

# Copy the published application from the build stage.
COPY --from=build /app/publish .

# Expose the port our application will run on.
EXPOSE 8080

# The command to start our application.
ENTRYPOINT ["dotnet", "order-service.dll"]
