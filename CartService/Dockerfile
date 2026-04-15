FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 80

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["cart-service.csproj", "./"]
RUN dotnet restore "cart-service.csproj"
COPY . .
RUN dotnet build "cart-service.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "cart-service.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "cart-service.dll"]