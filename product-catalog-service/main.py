# main.py
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, text # <--- ADDED 'text' HERE
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
import os
import logging

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Database Configuration ---
# Get database credentials from environment variables for Docker/Kubernetes deployment
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+mysqlconnector://user:password@db:3306/ecommerce_db")

# SQLAlchemy Engine
# The `pool_pre_ping=True` helps with connection stability in long-running services
# The `pool_recycle=3600` recycles connections after an hour, preventing stale connections
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Database Model (SQLAlchemy) ---
class Product(Base):
    """
    SQLAlchemy model for the 'products' table.
    Represents a product in the e-commerce catalog.
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, nullable=False)
    image_url = Column(String(512), nullable=True)
    category = Column(String(100), index=True, nullable=True)

# --- Pydantic Models (for Request/Response Validation) ---
class ProductBase(BaseModel):
    """Base Pydantic model for product data."""
    name: str
    description: Optional[str] = None
    price: float
    stock_quantity: int
    image_url: Optional[str] = None
    category: Optional[str] = None

class ProductCreate(ProductBase):
    """Pydantic model for creating a new product."""
    pass

class ProductUpdate(ProductBase):
    """Pydantic model for updating an existing product (all fields optional for partial update)."""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None
    image_url: Optional[str] = None
    category: Optional[str] = None

class ProductResponse(ProductBase):
    """Pydantic model for returning product data, including the ID."""
    id: int

    class Config:
        orm_mode = True # Enable ORM mode for SQLAlchemy integration

# --- FastAPI Application Setup ---
app = FastAPI(
    title="Product Catalog Service",
    description="Manages product data for the e-commerce application.",
    version="1.0.0"
)

# --- Database Dependency ---
def get_db():
    """
    Dependency to get a database session.
    Ensures the session is closed after the request is processed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Database Initialization (Run once on startup) ---
@app.on_event("startup")
async def startup_event():
    """
    Connects to the database and creates tables if they don't exist.
    Retries connection attempts to handle database startup delays.
    """
    logger.info("Attempting to connect to database and create tables...")
    retries = 5
    for i in range(retries):
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created or already exist.")
            return
        except OperationalError as e:
            logger.warning(f"Database connection failed (attempt {i+1}/{retries}): {e}")
            if i < retries - 1:
                import asyncio
                await asyncio.sleep(5) # Wait 5 seconds before retrying
            else:
                logger.error("Failed to connect to database after multiple retries. Exiting.")
                raise e
        except Exception as e:
            logger.error(f"An unexpected error occurred during database startup: {e}")
            raise e

# --- Health Check Endpoint ---
@app.get("/health", summary="Health Check", response_model=dict)
async def health_check():
    """
    Returns the health status of the service.
    Includes a basic database connection check.
    """
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1")) # <--- CHANGED THIS LINE
        db.close()
        logger.info("Health check successful.")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Service unhealthy: {e}")

# --- API Endpoints ---

@app.post("/products/", response_model=ProductResponse, status_code=201, summary="Create a new product")
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """
    Creates a new product in the database.
    """
    logger.info(f"Received request to create product: {product.name}")
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    logger.info(f"Product created with ID: {db_product.id}")
    return db_product

@app.get("/products/", response_model=List[ProductResponse], summary="Get all products")
async def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieves a list of all products with pagination.
    """
    logger.info(f"Received request to get products (skip={skip}, limit={limit})")
    products = db.query(Product).offset(skip).limit(limit).all()
    logger.info(f"Returning {len(products)} products.")
    return products

@app.get("/products/{product_id}", response_model=ProductResponse, summary="Get product by ID")
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a single product by its ID.
    Raises a 404 error if the product is not found.
    """
    logger.info(f"Received request to get product with ID: {product_id}")
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        logger.warning(f"Product with ID {product_id} not found.")
        raise HTTPException(status_code=404, detail="Product not found")
    logger.info(f"Returning product with ID: {product_id}")
    return product

@app.put("/products/{product_id}", response_model=ProductResponse, summary="Update an existing product")
async def update_product(product_id: int, product_update: ProductUpdate, db: Session = Depends(get_db)):
    """
    Updates an existing product by its ID.
    Only provided fields will be updated. Raises a 404 error if the product is not found.
    """
    logger.info(f"Received request to update product with ID: {product_id}")
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        logger.warning(f"Product with ID {product_id} not found for update.")
        raise HTTPException(status_code=404, detail="Product not found")

    # Update only the provided fields
    for key, value in product_update.dict(exclude_unset=True).items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)
    logger.info(f"Product with ID {product_id} updated successfully.")
    return db_product

@app.delete("/products/{product_id}", status_code=204, summary="Delete a product")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """
    Deletes a product by its ID.
    Raises a 404 error if the product is not found.
    """
    logger.info(f"Received request to delete product with ID: {product_id}")
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        logger.warning(f"Product with ID {product_id} not found for deletion.")
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(db_product)
    db.commit()
    logger.info(f"Product with ID {product_id} deleted successfully.")
    return {"message": "Product deleted successfully"}

# --- OpenTelemetry Placeholder (for future integration) ---
# To integrate OpenTelemetry for distributed tracing and metrics,
# you would typically add middleware and instrumentations here.
# Example (conceptual, requires OpenTelemetry packages):
# from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
# from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
# from opentelemetry import trace
# from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
# from opentelemetry.sdk.resources import Resource
# from opentelemetry.sdk.trace import TracerProvider
# from opentelemetry.sdk.trace.export import BatchSpanProcessor
#
# @app.on_event("startup")
# async def setup_opentelemetry():
#     resource = Resource.create({"service.name": "product-catalog-service"})
#     provider = TracerProvider(resource=resource)
#     processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="otel-collector:4317"))
#     provider.add_span_processor(processor)
#     trace.set_tracer_provider(provider)
#
#     FastAPIInstrumentor.instrument_app(app)
#     SQLAlchemyInstrumentor().instrument(engine=engine)
#     logger.info("OpenTelemetry instrumentation configured.")
