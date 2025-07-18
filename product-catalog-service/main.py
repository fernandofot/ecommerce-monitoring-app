# main.py
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
import os
import logging
from fastapi.middleware.cors import CORSMiddleware
import asyncio # Import asyncio for async operations

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Database Configuration ---
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+mysqlconnector://user:password@db:3306/ecommerce_db")
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Database Model (SQLAlchemy) ---
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, nullable=False)
    image_url = Column(String(512), nullable=True) # Correct column name
    category = Column(String(100), index=True, nullable=True)

# --- Pydantic Models (for Request/Response Validation) ---
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock_quantity: int
    image_url: Optional[str] = None # Correct field name
    category: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None
    image_url: Optional[str] = None # Correct field name
    category: Optional[str] = None

class ProductResponse(ProductBase):
    id: int
    class Config:
        orm_mode = True
        # FastAPI V2 Pydantic models use from_attributes instead of orm_mode
        # If you are using Pydantic V2, this should be:
        # from_attributes = True

# --- FastAPI Application Setup ---
app = FastAPI(
    title="Product Catalog Service",
    description="Manages product data for the e-commerce application.",
    version="1.0.0"
)

# --- CORS Configuration ---
# This middleware allows your frontend to make requests to this backend.
# Using '*' for origins is fine for local development, but be more specific in production.
origins = [
    "http://localhost",
    "http://localhost:80", # Nginx listens on 80
    "http://localhost:3000", # React dev server (if running directly)
    "http://127.0.0.1",
    "http://127.0.0.1:80",
    "http://127.0.0.1:3000",
    "http://host.docker.internal", # For Docker Desktop internal networking
    "http://host.docker.internal:80",
    "http://host.docker.internal:3000",
    # You can keep this if you found your Docker VM IP, otherwise it's optional
    "http://172.17.0.1",
    "http://172.17.0.1:80",
    "http://172.17.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"], # Allow all headers
)
# --- END CORS Configuration ---

# --- Database Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Database Initialization (Run once on startup) ---
@app.on_event("startup")
async def startup_event():
    logger.info("Attempting to connect to database and create tables...")
    retries = 5
    for i in range(retries):
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created or already exist.")
            # Add some initial data if the table is empty
            db = SessionLocal()
            if db.query(Product).count() == 0:
                logger.info("Adding initial product data...")
                initial_products = [
                    Product(name="Laptop Pro X", description="Powerful laptop for professionals, with 16GB RAM and 512GB SSD.", price=1299.99, stock_quantity=50, image_url="https://placehold.co/600x400/000000/FFFFFF?text=Laptop+Pro+X", category="Electronics"),
                    Product(name="Wireless Mouse", description="Ergonomic wireless mouse with adjustable DPI.", price=25.99, stock_quantity=200, image_url="https://placehold.co/600x400/FF0000/FFFFFF?text=Wireless+Mouse", category="Accessories"),
                    Product(name="Mechanical Keyboard", description="RGB mechanical keyboard with clicky switches.", price=89.99, stock_quantity=75, image_url="https://placehold.co/600x400/00FF00/000000?text=Keyboard", category="Accessories"),
                    Product(name="USB-C Hub", description="Multi-port USB-C hub with HDMI, USB 3.0, and SD card reader.", price=45.00, stock_quantity=150, image_url="https://placehold.co/600x400/0000FF/FFFFFF?text=USB-C+Hub", category="Accessories"),
                    Product(name="4K Monitor", description="27-inch 4K UHD monitor with HDR support.", price=399.99, stock_quantity=30, image_url=None, category="Electronics") # CORRECTED: 'image' to 'image_url'
                ]
                db.add_all(initial_products)
                db.commit()
                logger.info(f"Added {len(initial_products)} initial products.")
            db.close()
            return
        except OperationalError as e:
            logger.warning(f"Database connection failed (attempt {i+1}/{retries}): {e}")
            if i < retries - 1:
                # Use asyncio.sleep for async functions
                await asyncio.sleep(5)
            else:
                logger.error("Failed to connect to database after multiple retries. Exiting.")
                raise e
        except Exception as e:
            logger.error(f"An unexpected error occurred during database startup: {e}")
            raise e

# --- Health Check Endpoint ---
@app.get("/health", summary="Health Check", response_model=dict)
async def health_check():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("Health check successful.")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Service unhealthy: {e}")

# --- API Endpoints ---

@app.post("/products/", response_model=ProductResponse, status_code=201, summary="Create a new product")
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    logger.info(f"Received request to create product: {product.name}")
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    logger.info(f"Product created with ID: {db_product.id}")
    return db_product

@app.get("/products/", response_model=List[ProductResponse], summary="Get all products")
async def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    logger.info(f"Received request to get products (skip={skip}, limit={limit})")
    products = db.query(Product).offset(skip).limit(limit).all()
    logger.info(f"Returning {len(products)} products.")
    return products

@app.get("/products/{product_id}", response_model=ProductResponse, summary="Get product by ID")
async def get_product(product_id: int, db: Session = Depends(get_db)):
    logger.info(f"Received request to get product with ID: {product_id}")
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None: # THIS LINE IS THE FIX
        logger.warning(f"Product with ID {product_id} not found.")
        raise HTTPException(status_code=404, detail="Product not found")
    logger.info(f"Returning product with ID: {product_id}")
    return product

@app.put("/products/{product_id}", response_model=ProductResponse, summary="Update an existing product")
async def update_product(product_id: int, product_update: ProductUpdate, db: Session = Depends(get_db)):
    logger.info(f"Received request to update product with ID: {product_id}")
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        logger.warning(f"Product with ID {product_id} not found for update.")
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in product_update.dict(exclude_unset=True).items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)
    logger.info(f"Product with ID {product_id} updated successfully.")
    return db_product

@app.delete("/products/{product_id}", status_code=204, summary="Delete a product")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    logger.info(f"Received request to delete product with ID: {product_id}")
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        logger.warning(f"Product with ID {product_id} not found for deletion.")
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(db_product)
    db.commit()
    logger.info(f"Product with ID {product_id} deleted successfully.")
    return {"message": "Product deleted successfully"}
    
