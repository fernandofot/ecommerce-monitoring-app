using Microsoft.AspNetCore.Mvc;

namespace order_service.Controllers;

[ApiController]
[Route("[controller]")]
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

    [HttpGet(Name = "GetOrders")]
    public IEnumerable<Order> Get()
    {
        return Enumerable.Range(1, 5).Select(index => new Order
        {
            OrderId = Guid.NewGuid(),
            OrderDate = DateOnly.FromDateTime(DateTime.Now.AddDays(index)),
            Status = Summaries[Random.Shared.Next(Summaries.Length)]
        })
        .ToArray();
    }
}
