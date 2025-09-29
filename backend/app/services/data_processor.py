import json
import hashlib
import re
from typing import Dict, List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models import Product, Variant, ReviewSummary, PriceHistory
from datetime import datetime, date


class DataProcessor:
    def __init__(self, db: Session):
        self.db = db

    async def process_product(self, data: Dict) -> Product:
        """Process scraped product JSON and create/update database records"""

        # Extract base product information
        base_product = data.get('base_product', {})

        # Create or update product
        product = await self._process_base_product(base_product)

        # Process variants
        variants_data = data.get('variants', [])
        for variant_data in variants_data:
            await self._process_variant(product.id, variant_data)

        # Process reviews if available
        reviews_data = data.get('reviews', {})
        if reviews_data:
            await self._process_reviews(product.id, reviews_data)

        self.db.commit()
        return product

    async def _process_base_product(self, base_product: Dict) -> Product:
        """Process base product information"""

        base_sku = base_product.get('base_sku')
        if not base_sku:
            raise ValueError("base_sku is required")

        # Check if product already exists
        product = self.db.query(Product).filter_by(base_sku=base_sku).first()

        if not product:
            product = Product(
                brand=self._extract_brand(base_product),
                model_family=self._extract_model_family(base_product),
                base_sku=base_sku,
                product_name=base_product.get('product_name', ''),
                product_url=base_product.get('product_url'),
                pdf_spec_url=base_product.get('pdf_spec_url'),
                base_price=self._parse_price(base_product.get('base_price')),
                original_price=self._parse_price(base_product.get('original_price')),
                status=base_product.get('status', 'Unknown'),
                badges=base_product.get('badges', []),
                offers=base_product.get('offers', [])
            )
            self.db.add(product)
            self.db.flush()  # Get the ID
        else:
            # Update existing product
            product.product_name = base_product.get('product_name', product.product_name)
            product.product_url = base_product.get('product_url', product.product_url)
            product.base_price = self._parse_price(base_product.get('base_price')) or product.base_price
            product.original_price = self._parse_price(base_product.get('original_price')) or product.original_price
            product.status = base_product.get('status', product.status)
            product.badges = base_product.get('badges', product.badges)
            product.offers = base_product.get('offers', product.offers)

        return product

    async def _process_variant(self, product_id: str, variant_data: Dict):
        """Process individual variant"""

        variant_sku = variant_data.get('variant_sku')
        if not variant_sku:
            # Generate SKU if not provided
            variant_sku = f"{product_id}_{hashlib.md5(str(variant_data).encode()).hexdigest()[:8]}"

        # Generate configuration hash for deduplication
        config_hash = self._generate_config_hash(variant_data)

        # Check if variant exists by SKU or config hash
        variant = self.db.query(Variant).filter(
            (Variant.variant_sku == variant_sku) |
            (Variant.configuration_hash == config_hash)
        ).first()

        if not variant:
            # Parse specifications
            parsed_specs = self._parse_specifications(variant_data)

            variant = Variant(
                product_id=product_id,
                variant_sku=variant_sku,
                processor=variant_data.get('Processor') or variant_data.get('processor'),
                processor_family=parsed_specs.get('processor_family'),
                processor_speed=parsed_specs.get('processor_speed'),
                memory=variant_data.get('Memory') or variant_data.get('memory'),
                memory_size=parsed_specs.get('memory_size'),
                memory_type=parsed_specs.get('memory_type'),
                storage=variant_data.get('Storage') or variant_data.get('storage'),
                storage_size=parsed_specs.get('storage_size'),
                storage_type=parsed_specs.get('storage_type'),
                display=variant_data.get('Display') or variant_data.get('display'),
                display_size=parsed_specs.get('display_size'),
                display_resolution=parsed_specs.get('display_resolution'),
                graphics=variant_data.get('Graphics') or variant_data.get('graphics'),
                additional_features=self._extract_additional_features(variant_data),
                price=self._parse_price(variant_data.get('Price') or variant_data.get('price')),
                availability=variant_data.get('availability', 'Unknown'),
                configuration_hash=config_hash
            )
            self.db.add(variant)
            self.db.flush()

            # Add initial price history entry
            if variant.price:
                await self._add_price_history(variant.id, variant.price)

        else:
            # Update existing variant
            current_price = self._parse_price(variant_data.get('Price') or variant_data.get('price'))
            if current_price and current_price != variant.price:
                variant.price = current_price
                await self._add_price_history(variant.id, current_price)

            variant.availability = variant_data.get('availability', variant.availability)

    async def _add_price_history(self, variant_id: str, price: Decimal):
        """Add price history entry"""
        today = date.today()

        # Check if we already have a price entry for today
        existing_entry = self.db.query(PriceHistory).filter(
            PriceHistory.variant_id == variant_id,
            PriceHistory.captured_date == today
        ).first()

        if not existing_entry:
            price_entry = PriceHistory(
                variant_id=variant_id,
                price=price,
                captured_date=today
            )
            self.db.add(price_entry)

    def _parse_specifications(self, variant_data: Dict) -> Dict:
        """Parse and normalize specifications"""
        specs = {}

        # Parse processor
        processor = variant_data.get('Processor') or variant_data.get('processor', '')
        if processor:
            specs.update(self._parse_processor(processor))

        # Parse memory
        memory = variant_data.get('Memory') or variant_data.get('memory', '')
        if memory:
            specs.update(self._parse_memory(memory))

        # Parse storage
        storage = variant_data.get('Storage') or variant_data.get('storage', '')
        if storage:
            specs.update(self._parse_storage(storage))

        # Parse display
        display = variant_data.get('Display') or variant_data.get('display', '')
        if display:
            specs.update(self._parse_display(display))

        return specs

    def _parse_processor(self, processor: str) -> Dict:
        """Parse processor string"""
        specs = {}

        # Extract family
        if 'Intel Core Ultra' in processor:
            specs['processor_family'] = 'Intel Core Ultra'
        elif 'Intel Core i' in processor:
            if 'i3' in processor:
                specs['processor_family'] = 'Intel Core i3'
            elif 'i5' in processor:
                specs['processor_family'] = 'Intel Core i5'
            elif 'i7' in processor:
                specs['processor_family'] = 'Intel Core i7'
            elif 'i9' in processor:
                specs['processor_family'] = 'Intel Core i9'
            else:
                specs['processor_family'] = 'Intel Core i-series'
        elif 'AMD Ryzen' in processor:
            if 'Ryzen 3' in processor:
                specs['processor_family'] = 'AMD Ryzen 3'
            elif 'Ryzen 5' in processor:
                specs['processor_family'] = 'AMD Ryzen 5'
            elif 'Ryzen 7' in processor:
                specs['processor_family'] = 'AMD Ryzen 7'
            elif 'Ryzen 9' in processor:
                specs['processor_family'] = 'AMD Ryzen 9'
            else:
                specs['processor_family'] = 'AMD Ryzen'

        # Extract speed
        speed_match = re.search(r'(\d+\.?\d*)\s*GHz', processor, re.IGNORECASE)
        if speed_match:
            specs['processor_speed'] = f"{speed_match.group(1)} GHz"

        return specs

    def _parse_memory(self, memory: str) -> Dict:
        """Parse memory string"""
        specs = {}

        # Extract size
        size_match = re.search(r'(\d+)\s*GB', memory, re.IGNORECASE)
        if size_match:
            specs['memory_size'] = int(size_match.group(1))

        # Extract type
        if 'DDR5' in memory.upper():
            specs['memory_type'] = 'DDR5'
        elif 'DDR4' in memory.upper():
            specs['memory_type'] = 'DDR4'
        elif 'DDR3' in memory.upper():
            specs['memory_type'] = 'DDR3'

        return specs

    def _parse_storage(self, storage: str) -> Dict:
        """Parse storage string"""
        specs = {}

        # Extract size
        size_match = re.search(r'(\d+)\s*(GB|TB)', storage, re.IGNORECASE)
        if size_match:
            size = int(size_match.group(1))
            unit = size_match.group(2).upper()
            specs['storage_size'] = size * 1000 if unit == 'TB' else size

        # Extract type
        storage_upper = storage.upper()
        if 'NVME' in storage_upper:
            specs['storage_type'] = 'NVMe SSD'
        elif 'PCIe' in storage_upper and 'SSD' in storage_upper:
            specs['storage_type'] = 'PCIe SSD'
        elif 'SSD' in storage_upper:
            specs['storage_type'] = 'SSD'
        elif 'HDD' in storage_upper:
            specs['storage_type'] = 'HDD'
        elif 'EMMC' in storage_upper:
            specs['storage_type'] = 'eMMC'

        return specs

    def _parse_display(self, display: str) -> Dict:
        """Parse display string"""
        specs = {}

        # Extract size
        size_match = re.search(r'(\d+\.?\d*)[″"\s]*(?:inch|in)', display, re.IGNORECASE)
        if size_match:
            specs['display_size'] = float(size_match.group(1))

        # Extract resolution
        display_upper = display.upper()
        if 'WUXGA' in display_upper:
            specs['display_resolution'] = 'WUXGA'
        elif 'WQXGA' in display_upper:
            specs['display_resolution'] = 'WQXGA'
        elif 'FHD' in display_upper or '1920' in display:
            specs['display_resolution'] = 'FHD'
        elif 'HD' in display_upper:
            specs['display_resolution'] = 'HD'
        elif '4K' in display_upper:
            specs['display_resolution'] = '4K'

        return specs

    def _extract_additional_features(self, variant_data: Dict) -> Dict:
        """Extract additional features as boolean flags"""
        features = {}

        # Combine all text fields for feature detection
        all_text = ' '.join(str(v) for v in variant_data.values() if v).lower()

        # Feature detection
        features['has_touchscreen'] = any(term in all_text for term in ['touch', 'touchscreen'])
        features['has_fingerprint'] = any(term in all_text for term in ['fingerprint', 'biometric'])
        features['has_backlit_keyboard'] = any(term in all_text for term in ['backlit', 'backlight'])
        features['has_thunderbolt'] = any(term in all_text for term in ['thunderbolt', 'tb3', 'tb4'])
        features['has_usb_c'] = any(term in all_text for term in ['usb-c', 'usb c', 'type-c'])
        features['has_hdmi'] = 'hdmi' in all_text
        features['has_ethernet'] = any(term in all_text for term in ['ethernet', 'rj45'])
        features['has_wifi6'] = any(term in all_text for term in ['wifi 6', 'wi-fi 6', '802.11ax'])

        return features

    def _generate_config_hash(self, variant_data: Dict) -> str:
        """Generate unique hash for configuration"""
        # Use key specification fields for hashing
        config_items = [
            variant_data.get('Processor', '') or variant_data.get('processor', ''),
            variant_data.get('Memory', '') or variant_data.get('memory', ''),
            variant_data.get('Storage', '') or variant_data.get('storage', ''),
            variant_data.get('Display', '') or variant_data.get('display', ''),
            variant_data.get('Graphics', '') or variant_data.get('graphics', '')
        ]

        config_str = '|'.join(config_items)
        return hashlib.sha256(config_str.encode('utf-8')).hexdigest()

    def _parse_price(self, price_str) -> Optional[Decimal]:
        """Parse price string to Decimal"""
        if not price_str:
            return None

        # Handle various price formats
        if isinstance(price_str, (int, float)):
            return Decimal(str(price_str))

        # Remove currency symbols and commas
        price_clean = re.sub(r'[^\d.]', '', str(price_str))

        try:
            return Decimal(price_clean) if price_clean else None
        except:
            return None

    def _extract_brand(self, product_data: Dict) -> str:
        """Extract brand from product data"""
        name = product_data.get('product_name', '').lower()
        base_sku = product_data.get('base_sku', '').lower()

        if 'hp' in name or 'hp' in base_sku:
            return 'HP'
        elif any(term in name for term in ['lenovo', 'thinkpad']) or 'lenovo' in base_sku:
            return 'Lenovo'
        elif 'dell' in name or 'dell' in base_sku:
            return 'Dell'
        else:
            return 'Unknown'

    def _extract_model_family(self, product_data: Dict) -> str:
        """Extract model family from product data"""
        name = product_data.get('product_name', '')

        # HP patterns
        if 'ProBook 440 G11' in name:
            return 'ProBook 440 G11'
        elif 'ProBook 450 G10' in name:
            return 'ProBook 450 G10'
        elif 'EliteBook' in name:
            return 'EliteBook'
        elif 'ProBook' in name:
            # Extract generic ProBook model
            probook_match = re.search(r'ProBook\s+(\d+\s+G\d+)', name)
            if probook_match:
                return f'ProBook {probook_match.group(1)}'
            return 'ProBook'

        # Lenovo patterns
        elif 'ThinkPad E14 Gen 5' in name:
            if 'Intel' in name:
                return 'ThinkPad E14 Gen 5 Intel'
            elif 'AMD' in name:
                return 'ThinkPad E14 Gen 5 AMD'
            return 'ThinkPad E14 Gen 5'
        elif 'ThinkPad' in name:
            # Extract generic ThinkPad model
            thinkpad_match = re.search(r'ThinkPad\s+([A-Z]\d+(?:\s+Gen\s+\d+)?)', name)
            if thinkpad_match:
                return f'ThinkPad {thinkpad_match.group(1)}'
            return 'ThinkPad'

        return 'Unknown Model'

    async def _process_reviews(self, product_id: str, reviews_data: Dict):
        """Process review data for a product"""
        # Check if review summary exists
        review_summary = self.db.query(ReviewSummary).filter_by(product_id=product_id).first()

        if not review_summary:
            review_summary = ReviewSummary(product_id=product_id)
            self.db.add(review_summary)

        # Update review metrics
        review_summary.total_reviews = reviews_data.get('total', 0)
        review_summary.average_rating = Decimal(str(reviews_data.get('average', 0)))
        review_summary.rating_distribution = reviews_data.get('distribution', {})
        review_summary.sample_reviews = reviews_data.get('samples', [])

        # Extract pros and cons from sample reviews
        pros, cons = self._extract_pros_cons(reviews_data.get('samples', []))
        review_summary.top_pros = pros
        review_summary.top_cons = cons

    def _extract_pros_cons(self, sample_reviews: List[Dict]) -> tuple:
        """Extract common pros and cons from sample reviews"""
        pros = []
        cons = []

        for review in sample_reviews:
            content = review.get('content', '').lower()

            # Simple keyword-based extraction
            if any(word in content for word in ['fast', 'quick', 'speed', 'performance']):
                pros.append('Good performance')

            if any(word in content for word in ['battery', 'long lasting']):
                pros.append('Good battery life')

            if any(word in content for word in ['build quality', 'solid', 'sturdy']):
                pros.append('Solid build quality')

            if any(word in content for word in ['expensive', 'price', 'cost']):
                cons.append('Price could be better')

            if any(word in content for word in ['heavy', 'weight']):
                cons.append('Somewhat heavy')

        # Remove duplicates and limit
        pros = list(set(pros))[:5]
        cons = list(set(cons))[:5]

        return pros, cons

    async def bulk_process_json_files(self, file_paths: List[str]) -> Dict:
        """Process multiple JSON files in bulk"""
        results = {
            'processed': 0,
            'errors': 0,
            'products': [],
            'variants': 0
        }

        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                product = await self.process_product(data)
                results['products'].append(product.id)
                results['variants'] += len(product.variants)
                results['processed'] += 1

            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                results['errors'] += 1

        return results