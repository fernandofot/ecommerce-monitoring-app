# main.py

# A whole lot of imports. This is a common sight in FastAPI projects!
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
import asyncio # We'll need this for waiting on the database to start up

# --- Basic Logging Setup ---
# This is a good starting point for local development.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Database Stuff ---
# Let's grab the DB URL from the environment, with a local default for testing.
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+mysqlconnector://user:password@db:3306/ecommerce_db")
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
db_session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Database Model (The actual table structure) ---
# This defines our `products` table.
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, nullable=False)
    image_url = Column(String(512), nullable=True)
    category = Column(String(100), index=True, nullable=True)

# --- Pydantic Models (For validating data) ---
# These models ensure that the data we get and send is in the right shape.
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock_quantity: int
    image_url: Optional[str] = None
    category: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None
    image_url: Optional[str] = None
    category: Optional[str] = None

class ProductResponse(ProductBase):
    id: int
    class Config:
        orm_mode = True
        # NOTE: If you're on a newer Pydantic, you'll need to use `from_attributes = True` instead of `orm_mode`.
        # Just a heads up in case you see errors!

# A model for the "add to cart" request. Simple stuff.
class AddToCartRequest(BaseModel):
    product_id: int

# --- FastAPI App Setup ---
# Let's get our FastAPI app instance ready.
app = FastAPI(
    title="Product Catalog Service",
    description="Manages product data for the e-commerce application.",
    version="1.0.0",
    # This is important! The Nginx proxy will serve this under /api/.
    # Telling FastAPI about this makes sure all the docs and links are correct.
    root_path="/api",
)

# --- CORS Configuration ---
# CORS is always a headache. This is the "dev mode" configuration to
# make sure the frontend can talk to the backend without issues.
# IMPORTANT: You'll want to lock this down in a real production environment.
origins = [
    "http://localhost",
    "http://localhost:80",
    "http://localhost:3000",
    "http://127.0.0.1",
    "http://127.0.0.1:80",
    "http://127.0.0.1:3000",
    "http://host.docker.internal",
    "http://host.docker.internal:80",
    "http://host.docker.internal:3000",
    "http://172.17.0.1", # In case we need the Docker bridge network IP
    "http://172.17.0.1:80",
    "http://172.17.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- END CORS Configuration ---

# --- Database Dependency ---
# This is a cool FastAPI pattern to handle database sessions automatically.
def get_db():
    db = db_session_factory()
    try:
        yield db
    finally:
        db.close()

# --- Database Initialization (Runs when the app starts up) ---
@app.on_event("startup")
async def startup_event():
    logger.info("Attempting to connect to the database and set up tables...")
    retries = 5
    for i in range(retries):
        try:
            # Create all the tables defined by our SQLAlchemy models.
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created or already exist.")

            # Let's throw in some dummy data if the table is empty, so we have something to see!
            db = db_session_factory()
            if db.query(Product).count() == 0:
                logger.info("Adding some initial product data...")
                initial_products = [
                    Product(name="Laptop Pro X", description="Powerful laptop for professionals, with 16GB RAM and 512GB SSD.", price=1299.99, stock_quantity=50, image_url="https://placehold.co/600x400/000000/FFFFFF?text=Laptop+Pro+X", category="Electronics"),
                    Product(name="Wireless Mouse", description="Ergonomic wireless mouse with adjustable DPI.", price=25.99, stock_quantity=200, image_url="https://placehold.co/600x400/FF0000/FFFFFF?text=Wireless+Mouse", category="Accessories"),
                    Product(name="Mechanical Keyboard", description="RGB mechanical keyboard with clicky switches.", price=89.99, stock_quantity=75, image_url="https://placehold.co/600x400/00FF00/000000?text=Keyboard", category="Accessories"),
                    Product(name="USB-C Hub", description="Multi-port USB-C hub with HDMI, USB 3.0, and SD card reader.", price=45.00, stock_quantity=150, image_url="https://placehold.co/600x400/0000FF/FFFFFF?text=USB-C+Hub", category="Accessories"),
                    Product(name="4K Monitor", description="27-inch 4K UHD monitor with HDR support.", price=399.99, stock_quantity=30, image_url=None, category="Electronics")
                ]
                db.add_all(initial_products)
                db.commit()
                logger.info(f"Added {len(initial_products)} initial products.")
            db.close()
            return
        except OperationalError as e:
            logger.warning(f"Database connection failed (attempt {i+1}/{retries}). It might not be ready yet: {e}")
            if i < retries - 1:
                await asyncio.sleep(5) # Wait a bit before trying again.
            else:
                logger.error("Failed to connect to the database after too many retries. Giving up.")
                raise e
        except Exception as e:
            logger.error(f"Something unexpected went wrong during startup: {e}")
            raise e

# --- Health Check Endpoint ---
# A simple endpoint to make sure the app is alive and can talk to the database.
@app.get("/health", summary="Health Check", response_model=dict)
async def health_check():
    try:
        db = db_session_factory()
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("Health check passed.")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed! The database might be down: {e}")
        raise HTTPException(status_code=500, detail=f"Service unhealthy: {e}")

# --- API Endpoints ---
# The actual logic for our e-commerce API.

@app.post("/products/", response_model=ProductResponse, status_code=201, summary="Create a new product")
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    logger.info(f"Adding a new product: {product.name}")
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    logger.info(f"New product created with ID: {db_product.id}")
    return db_product

@app.get("/products/", response_model=List[ProductResponse], summary="Get all products")
async def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    logger.info(f"Fetching products from the database (skip={skip}, limit={limit}).")
    products = db.query(Product).offset(skip).limit(limit).all()
    logger.info(f"Found {len(products)} products.")
    return products

@app.get("/products/{product_id}", response_model=ProductResponse, summary="Get product by ID")
async def get_product(product_id: int, db: Session = Depends(get_db)):
    logger.info(f"Looking for product with ID: {product_id}")
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        logger.warning(f"Couldn't find a product with ID {product_id}.")
        raise HTTPException(status_code=404, detail="Product not found")
    logger.info(f"Found product with ID: {product_id}")
    return product

@app.put("/products/{product_id}", response_model=ProductResponse, summary="Update an existing product")
async def update_product(product_id: int, product_update: ProductUpdate, db: Session = Depends(get_db)):
    logger.info(f"Updating product with ID: {product_id}")
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        logger.warning(f"Product with ID {product_id} not found, so we can't update it.")
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in product_update.dict(exclude_unset=True).items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)
    logger.info(f"Product {product_id} updated successfully.")
    return db_product

@app.delete("/products/{product_id}", status_code=204, summary="Delete a product")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    logger.info(f"Attempting to delete product with ID: {product_id}")
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        logger.warning(f"Product with ID {product_id} not found, nothing to delete.")
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(db_product)
    db.commit()
    logger.info(f"Product {product_id} deleted.")
    return {"message": "Product deleted successfully"}

@app.post("/cart/add", summary="Add a product to the cart", status_code=200)
async def add_to_cart(request: AddToCartRequest):
    """
    This endpoint is just a simulation for now!
    In a real app, this would be a much more complex process involving
    inventory checks, user sessions, and maybe even a separate microservice.
    For this demo, we'll just pretend it worked.
    """
    logger.info(f"Simulating adding product ID {request.product_id} to cart.")
    return {"message": f"Product ID {request.product_id} successfully added to cart (simulated)."}
