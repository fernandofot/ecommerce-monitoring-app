namespace order_service;

public class Order
{
    public Guid OrderId { get; set; }
    public DateOnly OrderDate { get; set; }
    public string? Status { get; set; }
}
