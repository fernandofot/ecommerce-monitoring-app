using Microsoft.AspNetCore.Mvc;
using StackExchange.Redis;
using System.Text.Json;
using CartService.Models;
using System.Text;

namespace CartService.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class CartController : ControllerBase
    {
        private readonly IConnectionMultiplexer _redis;
        private readonly ILogger<CartController> _logger;

        public CartController(IConnectionMultiplexer redis, ILogger<CartController> logger)
        {
            _redis = redis;
            _logger = logger;
        }

        [HttpGet("{userId}")]
        public async Task<ActionResult<Cart>> GetCart(string userId)
        {
            var db = _redis.GetDatabase();
            var cartData = await db.StringGetAsync($"cart:{userId}");

            if (cartData.IsNullOrEmpty)
            {
                return Ok(new Cart { UserId = userId });
            }

            var cart = JsonSerializer.Deserialize<Cart>(cartData);
            return Ok(cart);
        }

        [HttpPost("{userId}/items")]
        public async Task<ActionResult> AddToCart(string userId, [FromBody] CartItem item)
        {
            var db = _redis.GetDatabase();
            var cartData = await db.StringGetAsync($"cart:{userId}");

            Cart cart;
            if (cartData.IsNullOrEmpty)
            {
                cart = new Cart { UserId = userId };
            }
            else
            {
                cart = JsonSerializer.Deserialize<Cart>(cartData);
            }

            var existingItem = cart.Items.FirstOrDefault(i => i.ProductId == item.ProductId);
            if (existingItem != null)
            {
                existingItem.Quantity += item.Quantity;
            }
            else
            {
                cart.Items.Add(item);
            }

            var serializedCart = JsonSerializer.Serialize(cart);
            await db.StringSetAsync($"cart:{userId}", serializedCart);

            _logger.LogInformation($"Added item to cart for user {userId}");
            return Ok(cart);
        }

        [HttpDelete("{userId}")]
        public async Task<ActionResult> ClearCart(string userId)
        {
            var db = _redis.GetDatabase();
            await db.KeyDeleteAsync($"cart:{userId}");

            _logger.LogInformation($"Cart cleared for user {userId}");
            return Ok(new { message = "Cart cleared successfully" });
        }

        [HttpPost("{userId}/checkout")]
        public async Task<ActionResult<OrderConfirmation>> Checkout(string userId)
        {
            // 1. Fetch cart from Redis
            var db = _redis.GetDatabase();
            var cartData = await db.StringGetAsync($"cart:{userId}");

            if (cartData.IsNullOrEmpty)
            {
                return BadRequest("Cart is empty.");
            }

            // Deserialize cart (null-check to satisfy nullable warnings)
            var cart = JsonSerializer.Deserialize<Cart>(cartData);
            if (cart == null || cart.Items == null || !cart.Items.Any())
            {
                return BadRequest("Cart has no items.");
            }

            // 2. Transform cart items to order items
            // NOTE: use the correct property name from your CartItem model (likely UnitPrice)
            var orderItems = cart.Items.Select(item => new OrderItemDto
            {
                ProductId = item.ProductId,
                ProductName = item.ProductName,
                Quantity = item.Quantity,
                UnitPrice = item.UnitPrice // <-- replace 'Price' with 'UnitPrice' (or the correct property)
            }).ToList();

            // 3. Prepare order request
            var createOrderRequest = new CreateOrderRequest
            {
                UserId = userId,
                Items = orderItems
            };

            // 4. Send to Order Service
            using var httpClient = new HttpClient();

            var json = JsonSerializer.Serialize(createOrderRequest);
            _logger.LogInformation("CartService: sending order to Order Service for user {UserId} - payload: {Payload}", userId, json);

            var content = new StringContent(json, Encoding.UTF8, "application/json");
            var response = await httpClient.PostAsync("http://order-service/orders", content);

            if (!response.IsSuccessStatusCode)
            {
                _logger.LogError("Failed to create order. StatusCode: {StatusCode}", response.StatusCode);
                return StatusCode((int)response.StatusCode, "Failed to process order");
            }

            // 5. Read order response (null-safe)
            var responseContent = await response.Content.ReadAsStringAsync();
            var order = JsonSerializer.Deserialize<Order>(responseContent);
            if (order == null)
            {
                _logger.LogError("Order Service returned an empty/invalid response.");
                return StatusCode(502, "Invalid response from order service");
            }

            // 6. Clear cart after successful order
            await db.KeyDeleteAsync($"cart:{userId}");

            // 7. Return confirmation
            return Ok(new OrderConfirmation
            {
                OrderId = order.OrderId,
                Message = "Order placed successfully"
            });
        }
    }  

    // Supporting Models
    public class OrderItemDto
    {
        public string ProductId { get; set; } = default!;
        public string ProductName { get; set; } = default!;
        public int Quantity { get; set; }
        public decimal UnitPrice { get; set; }
    }

    public class CreateOrderRequest
    {
        public string UserId { get; set; } = default!;
        public List<OrderItemDto> Items { get; set; } = new();
    }

    public class OrderConfirmation
    {
        public Guid OrderId { get; set; }
        public string Message { get; set; } = default!;
    }

    public class Order
    {
        public Guid OrderId { get; set; }
        public DateTime OrderDate { get; set; }
        public string Status { get; set; } = default!;
        public List<OrderItemDto> Items { get; set; } = new();
        public decimal TotalAmount { get; set; }
    }
}