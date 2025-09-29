"""
Data loader for sample data
"""

import logging
from sqlalchemy.orm import Session
from app.models import Product, Variant

logger = logging.getLogger(__name__)


def load_sample_data(db: Session):
    """Load sample data into the database"""
    try:
        # Check if data already exists
        if db.query(Product).count() > 0:
            logger.info("Sample data already loaded")
            return

        # Add sample products here if needed
        logger.info("Loading sample data...")

        # Sample HP laptop
        hp_product = Product(
            brand="HP",
            model_family="ProBook 450 G10",
            base_sku="HP-PB450-G10",
            product_name="HP ProBook 450 G10 Business Laptop",
            base_price=899.99,
            status="In Stock"
        )
        db.add(hp_product)
        db.commit()

        # Sample Lenovo laptop
        lenovo_product = Product(
            brand="Lenovo",
            model_family="ThinkPad E14",
            base_sku="LEN-TP-E14",
            product_name="Lenovo ThinkPad E14 Gen 5",
            base_price=799.99,
            status="In Stock"
        )
        db.add(lenovo_product)
        db.commit()

        logger.info("Sample data loaded successfully")

    except Exception as e:
        logger.error(f"Error loading sample data: {e}")
        db.rollback()
        raise