// Models.cs
// This file defines the data models for our Order Processing Service.
// These models will be used by Entity Framework Core to create and manage
// the database tables.

using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace order_service.Models
{
    // The [Table("orders")] attribute specifies the table name in the database.
    [Table("orders")]
    public class Order
    {
        [Key]
        [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
        public int Id { get; set; }

        public string UserId { get; set; } = string.Empty;

        public DateTime OrderDate { get; set; }

        // The total amount of the order.
        public decimal TotalAmount { get; set; }

        // Navigation property to hold the collection of order items.
        public List<OrderItem> Items { get; set; } = new List<OrderItem>();
    }

    // The [Table("order_items")] attribute specifies the table name in the database.
    [Table("order_items")]
    public class OrderItem
    {
        [Key]
        [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
        public int Id { get; set; }

        // Foreign key to the Order table.
        [ForeignKey("Order")]
        public int OrderId { get; set; }
        
        // Navigation property for the parent Order.
        public Order? Order { get; set; }

        public string ProductId { get; set; } = string.Empty;

        public int Quantity { get; set; }

        public decimal Price { get; set; }
    }
}
