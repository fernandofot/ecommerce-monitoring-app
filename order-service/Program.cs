var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

// ===== Diagnostic logging middleware (NEW) =====
app.Use(async (context, next) =>
{
    var logger = context.RequestServices.GetRequiredService<ILoggerFactory>()
        .CreateLogger("RequestLogger");
    logger.LogInformation("Order service received: {Method} {Path}",
        context.Request.Method, context.Request.Path);
    await next();
});
// ===============================================

app.UseHttpsRedirection();

app.UseAuthorization();

// This maps our controllers (including OrdersController with [Route("orders")])
app.MapControllers();

app.Run();