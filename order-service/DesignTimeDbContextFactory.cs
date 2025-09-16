// DesignTimeDbContextFactory.cs
// This factory explicitly provides the connection string for the `dotnet ef`
// command-line tool, ensuring it can connect to the database at design time.

using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Design;
using order_service.Context;

namespace order_service
{
    public class DesignTimeDbContextFactory : IDesignTimeDbContextFactory<OrderContext>
    {
        public OrderContext CreateDbContext(string[] args)
        {
            // The connection string needed for the local machine to connect
            // to the database running inside the Docker container.
            const string connectionString = "Server=localhost;Port=3306;Database=ecommerce_db;Uid=user;Pwd=password;";

            // We must create the DbContextOptions explicitly, as the design-time tool
            // does not have access to our service provider.
            var optionsBuilder = new DbContextOptionsBuilder<OrderContext>();
            optionsBuilder.UseMySql(connectionString, ServerVersion.AutoDetect(connectionString));

            // Return a new instance of our DbContext.
            return new OrderContext(optionsBuilder.Options);
        }
    }
}