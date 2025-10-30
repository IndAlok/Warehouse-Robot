from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import Config

Base = declarative_base()

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    products = relationship('Product', back_populates='category')

class Location(Base):
    __tablename__ = 'locations'
    
    id = Column(Integer, primary_key=True)
    shelf_number = Column(Integer, nullable=False)
    block = Column(String(10), nullable=False)
    zone = Column(String(50))
    capacity = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    products = relationship('Product', back_populates='location')
    
    @property
    def full_location(self):
        return f"Shelf {self.shelf_number} in Block {self.block}"

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    sku = Column(String(50), unique=True, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=False)
    quantity = Column(Integer, default=0)
    price = Column(Float, default=0.0)
    barcode = Column(String(100))
    qr_code = Column(String(100), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    category = relationship('Category', back_populates='products')
    location = relationship('Location', back_populates='products')
    scans = relationship('ScanLog', back_populates='product')

class ScanLog(Base):
    __tablename__ = 'scan_logs'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=True)
    qr_data = Column(String(200), nullable=False)
    scanned_location_id = Column(Integer, ForeignKey('locations.id'), nullable=True)
    is_correct_location = Column(Boolean, default=False)
    status = Column(String(20), default='pending')
    message = Column(String(500))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    product = relationship('Product', back_populates='scans')

engine = create_engine(Config.DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)
    print("Database tables created successfully!")

def get_session():
    return Session()
