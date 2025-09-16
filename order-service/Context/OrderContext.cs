// OrderContext.cs
// This is the database context for our Order Processing Service.
// It defines the entities that Entity Framework Core will manage.

using Microsoft.EntityFrameworkCore;
using order_service.Models;

namespace order_service.Context
{
    public class OrderContext : DbContext
    {
        public OrderContext(DbContextOptions<OrderContext> options) : base(options)
        {
        }

        // A DbSet represents a collection of all entities in the context,
        // or that can be queried from the database, of a given type.
        public DbSet<Order> Orders { get; set; }
        public DbSet<OrderItem> OrderItems { get; set; }
    }
}
