using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.AspNetCore.Mvc;

namespace order_service.Controllers;

[ApiController]
// Accept both "/" and "/orders" at the controller level
[Route("")]
[Route("orders")]
public class OrdersController : ControllerBase
{
    private static readonly string[] Summaries = new[]
    {
        "New", "Processing", "Shipped", "Delivered", "Canceled"
    };

    private readonly ILogger<OrdersController> _logger;

    public OrdersController(ILogger<OrdersController> logger)
    {
        _logger = logger;
    }

    // ===== Demo GET endpoint =====

    // Map GET "/" and GET "/orders"
    [HttpGet]
    [Route("")]
    [Route("orders")]
    public IEnumerable<Order> Get()
    {
        return Enumerable.Range(1, 5).Select(index => new Order
        {
            OrderId = Guid.NewGuid(),
            OrderDate = DateTime.UtcNow.AddDays(index),
            Status = Summaries[Random.Shared.Next(Summaries.Length)],
            Items = new List<OrderItemDto>(),
            TotalAmount = 0
        })
        .ToArray();
    }

    // ===== Create an order (this is where we log cart contents) =====

    // Map POST "/" and POST "/orders"
    [HttpPost]
    [Route("")]
    [Route("orders")]
    public IActionResult CreateOrder([FromBody] CreateOrderRequest request)
    {
        if (request == null || request.Items == null || request.Items.Count == 0)
        {
            return BadRequest("Order must contain at least one item.");
        }

        // Calculate totals
        var totalAmount = request.Items.Sum(i => i.UnitPrice * i.Quantity);
        var totalItems = request.Items.Sum(i => i.Quantity);

        var order = new Order
        {
            OrderId = Guid.NewGuid(),
            OrderDate = DateTime.UtcNow,
            Status = "New",
            Items = request.Items,
            TotalAmount = totalAmount
        };

        // This is the important part for Dynatrace / Instana:
        // We emit a structured log with all the business info.
        _logger.LogInformation("OrderCreated {@OrderEvent}", new
        {
            Event = "order_created",
            UserId = request.UserId,
            OrderId = order.OrderId,
            TotalItems = totalItems,
            TotalAmount = totalAmount,
            Items = request.Items.Select(i => new
            {
                i.ProductId,
                i.ProductName,
                i.Quantity,
                i.UnitPrice
            })
        });

        return Ok(order);
    }
}

// ===== Simple models to represent an order and its items =====

// This is what the frontend / API gateway will send for each item in the cart.
public class OrderItemDto
{
    public string ProductId { get; set; } = default!;
    public string ProductName { get; set; } = default!;
    public int Quantity { get; set; }
    public decimal UnitPrice { get; set; }
}

// This is the payload of POST /orders
public class CreateOrderRequest
{
    public string UserId { get; set; } = default!;
    public List<OrderItemDto> Items { get; set; } = new();
}

// This is what the service returns as an "order"
public class Order
{
    public Guid OrderId { get; set; }
    public DateTime OrderDate { get; set; }
    public string Status { get; set; } = default!;
    public List<OrderItemDto> Items { get; set; } = new();
    public decimal TotalAmount { get; set; }
}