# main.py

# A whole lot of imports. This is a common sight in FastAPI projects!
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.exc import OperationalError
import os
import logging
from fastapi.middleware.cors import CORSMiddleware
import asyncio

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

# --- Database Models (The actual table structure) ---
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

# NEW! This is our model for a single item in a shopping cart.
# We're using a 'cart_session_id' to identify a cart, which is a good
# temporary solution until we build out proper user authentication.
class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True, index=True)
    cart_session_id = Column(String(255), index=True, nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, nullable=False, default=1)

    # This is the magic of 'relationship'. It lets us easily
    # get all the details of the product linked to this cart item!
    product = relationship("Product")

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

# NEW! A Pydantic model for our cart item response.
# Notice how it includes the full `ProductResponse` model? That's what `relationship` above lets us do!
class CartItemResponse(BaseModel):
    id: int
    cart_session_id: str
    product_id: int
    quantity: int
    product: ProductResponse
    class Config:
        orm_mode = True

# A model for the "add to cart" request. Simple stuff.
# Now it includes the session ID and an optional quantity.
class AddToCartRequest(BaseModel):
    product_id: int
    cart_session_id: str
    quantity: Optional[int] = 1

# NEW! A model for the "remove from cart" request.
class RemoveFromCartRequest(BaseModel):
    product_id: int
    cart_session_id: str

# NEW! A model for updating a cart item quantity.
# This matches the data the frontend is likely sending.
class UpdateCartQuantityRequest(BaseModel):
    cart_session_id: str
    product_id: int
    quantity: int

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
            # This will now create the 'products' AND 'cart_items' tables!
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

# --- API Endpoints for Products ---
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

# --- API Endpoints for Cart Management! ---
# These are the new routes for our cart functionality.

@app.post("/cart/add", response_model=CartItemResponse, status_code=201, summary="Add a product to a cart session")
async def add_to_cart(request: AddToCartRequest, db: Session = Depends(get_db)):
    logger.info(f"Adding product ID {request.product_id} to cart session {request.cart_session_id}.")

    product = db.query(Product).filter(Product.id == request.product_id).first()
    if not product:
        logger.warning(f"Product with ID {request.product_id} not found!")
        raise HTTPException(status_code=404, detail="Product not found")

    # Is there enough stock? This is a critical check!
    if product.stock_quantity < request.quantity:
        logger.warning(f"Not enough stock for product ID {request.product_id}. Requested: {request.quantity}, Available: {product.stock_quantity}")
        raise HTTPException(status_code=400, detail="Insufficient stock available")

    # Let's see if this product is already in the cart for this session.
    cart_item = db.query(CartItem).filter(
        CartItem.cart_session_id == request.cart_session_id,
        CartItem.product_id == request.product_id
    ).first()

    if cart_item:
        # If it's there, we just update the quantity. Easy!
        cart_item.quantity += request.quantity
    else:
        # If it's a brand new item, we create a new entry.
        cart_item = CartItem(
            cart_session_id=request.cart_session_id,
            product_id=request.product_id,
            quantity=request.quantity
        )
        db.add(cart_item)

    # NEW LOGIC: This is the crucial part that was missing!
    # Decrease the stock quantity on the product itself.
    product.stock_quantity -= request.quantity

    # Now, save all the changes to the database.
    db.commit()

    # Refresh the objects to get the latest data from the database.
    db.refresh(cart_item)
    db.refresh(product)

    logger.info(f"Product ID {request.product_id} added to cart and stock decreased to {product.stock_quantity}.")

    return cart_item

@app.get("/cart/{cart_session_id}", response_model=List[CartItemResponse], summary="Get all items in a cart session")
async def get_cart(cart_session_id: str, db: Session = Depends(get_db)):
    logger.info(f"Fetching cart for session ID: {cart_session_id}")
    # Here, we get all the cart items for the given session ID.
    cart_items = db.query(CartItem).filter(CartItem.cart_session_id == cart_session_id).all()
    if not cart_items:
        logger.info(f"Cart session {cart_session_id} not found. Returning an empty list, which is fine!")
        return []
    logger.info(f"Found {len(cart_items)} items for cart session {cart_session_id}.")
    return cart_items

# NEW ENDPOINT: Handles the POST request from the frontend to update quantity.
@app.post("/cart/update-quantity", response_model=CartItemResponse, summary="Update quantity of a product in the cart by session and product ID")
async def update_cart_item_quantity(request: UpdateCartQuantityRequest, db: Session = Depends(get_db)):
    logger.info(f"Received request to update product ID {request.product_id} for session {request.cart_session_id} to quantity {request.quantity}.")
    
    # We must find the existing cart item first.
    cart_item = db.query(CartItem).filter(
        CartItem.cart_session_id == request.cart_session_id,
        CartItem.product_id == request.product_id
    ).first()
    
    if not cart_item:
        logger.warning(f"Could not find cart item for product ID {request.product_id} in session {request.cart_session_id}.")
        raise HTTPException(status_code=404, detail="Cart item not found")

    # Get the related product to check stock.
    product = db.query(Product).filter(Product.id == cart_item.product_id).first()
    if not product:
        logger.error(f"Associated product not found for cart item ID {cart_item.id}.")
        raise HTTPException(status_code=500, detail="Associated product not found.")
        
    current_quantity = cart_item.quantity
    new_quantity = request.quantity

    if new_quantity < 0:
        raise HTTPException(status_code=400, detail="Quantity cannot be negative")
    
    # Calculate the change in quantity to update the stock.
    quantity_change = new_quantity - current_quantity
    
    if quantity_change > 0:
        # If increasing, check for sufficient stock.
        if product.stock_quantity < quantity_change:
            logger.warning(f"Insufficient stock for product ID {product.id}. Available: {product.stock_quantity}. Needed: {quantity_change}.")
            raise HTTPException(status_code=400, detail="Insufficient stock available.")
        product.stock_quantity -= quantity_change
    elif quantity_change < 0:
        # If decreasing, return stock.
        product.stock_quantity += abs(quantity_change)

    # Update the cart item quantity.
    cart_item.quantity = new_quantity
    
    # If the new quantity is 0, remove the item entirely.
    if new_quantity == 0:
        db.delete(cart_item)
        db.commit()
        logger.info(f"Removed item from cart for product ID {request.product_id}.")
        return {"message": "Cart item removed successfully"}
    
    # Commit the changes to the database.
    db.commit()
    db.refresh(cart_item)
    db.refresh(product)
    
    logger.info(f"Updated quantity for cart item {cart_item.id} to {new_quantity}. New product stock: {product.stock_quantity}.")
    return cart_item

@app.put("/cart/update/{cart_item_id}", response_model=CartItemResponse, summary="Update quantity of a product in the cart")
async def update_cart_item_quantity_by_id(cart_item_id: int, quantity: int, db: Session = Depends(get_db)):
    logger.info(f"Received request to update cart item {cart_item_id} to quantity {quantity}.")
    
    cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    # If the user sets the quantity to 0 or less, we should just remove the item.
    if quantity <= 0:
        db.delete(cart_item)
        db.commit()
        raise HTTPException(status_code=200, detail="Cart item removed")

    cart_item.quantity = quantity
    db.commit()
    db.refresh(cart_item)
    logger.info(f"Updated quantity for cart item {cart_item_id} to {quantity}.")
    return cart_item

@app.delete("/cart/item/{cart_item_id}", status_code=204, summary="Remove a product from the cart")
async def remove_from_cart(cart_item_id: int, db: Session = Depends(get_db)):
    logger.info(f"Removing cart item with ID: {cart_item_id}")
    
    cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
        
    db.delete(cart_item)
    db.commit()
    logger.info(f"Cart item with ID {cart_item_id} removed successfully.")
    # FastAPI returns a 204 No Content for a successful deletion, so no message needed.
    return {"message": "Cart item removed successfully"}

# NEW: Endpoint to handle POST requests from the frontend
@app.post("/cart/remove", status_code=200, summary="Remove a product from the cart by session ID and product ID")
async def remove_from_cart_by_session(request: RemoveFromCartRequest, db: Session = Depends(get_db)):
    logger.info(f"Attempting to remove product ID {request.product_id} from cart session {request.cart_session_id}.")
    
    # Find the specific cart item to delete
    cart_item = db.query(CartItem).filter(
        CartItem.cart_session_id == request.cart_session_id,
        CartItem.product_id == request.product_id
    ).first()

    if not cart_item:
        # If the item isn't in the cart, we can just return success and a message.
        logger.warning("Attempted to remove an item that was not in the cart.")
        raise HTTPException(status_code=404, detail="Item not found in cart")
    
    # Return the stock to the product before deleting the cart item
    product = db.query(Product).filter(Product.id == cart_item.product_id).first()
    if product:
        product.stock_quantity += cart_item.quantity
        db.refresh(product)
        logger.info(f"Returned {cart_item.quantity} units of stock for product ID {product.id}.")

    db.delete(cart_item)
    db.commit()
    logger.info(f"Successfully removed product ID {request.product_id} from cart.")

    return {"status": "ok", "message": "Item removed from cart."}
