from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.sql import func
from ..models.marketplace import Asset, AssetListing, Purchase, Review
from ..models.license import License, LicenseTransaction
from ..services.license_manager import LicenseManager
from .. import db

class MarketplaceService:
    def __init__(self, config: Dict):
        self.config = config
        self.marketplace_config = config.MARKETPLACE
        self.license_manager = LicenseManager(config)
        
    def list_asset(
        self,
        user_id: int,
        asset_data: Dict,
        price: float,
        currency: str = 'USD'
    ) -> Dict:
        """List a new asset on the marketplace"""
        # Validate inputs
        if currency not in self.marketplace_config['supported_currencies']:
            raise ValueError(f"Unsupported currency: {currency}")
            
        if price < self.marketplace_config['min_price']:
            raise ValueError(
                f"Price must be at least {self.marketplace_config['min_price']} {currency}"
            )
            
        # Create asset record
        asset = Asset(
            user_id=user_id,
            name=asset_data['name'],
            description=asset_data['description'],
            category=asset_data['category'],
            subcategory=asset_data.get('subcategory'),
            tags=asset_data.get('tags', []),
            preview_url=asset_data.get('preview_url'),
            file_url=asset_data['file_url'],
            file_size=asset_data['file_size'],
            format=asset_data['format']
        )
        
        # Create listing
        listing = AssetListing(
            asset=asset,
            price=price,
            currency=currency,
            status='active'
        )
        
        db.session.add(asset)
        db.session.add(listing)
        db.session.commit()
        
        return {
            'asset_id': asset.id,
            'listing_id': listing.id,
            'status': 'active'
        }
        
    def purchase_asset(
        self,
        user_id: int,
        listing_id: int,
        payment_info: Dict
    ) -> Dict:
        """Purchase an asset from the marketplace"""
        listing = AssetListing.query.get(listing_id)
        if not listing or listing.status != 'active':
            raise ValueError("Invalid or inactive listing")
            
        # Process payment
        payment_result = self._process_payment(
            user_id,
            listing.price,
            listing.currency,
            payment_info
        )
        
        # Create purchase record
        purchase = Purchase(
            user_id=user_id,
            listing_id=listing_id,
            price=listing.price,
            currency=listing.currency,
            payment_id=payment_result['payment_id']
        )
        
        # Acquire license
        license = self.license_manager.acquire_license(
            listing.asset.id,
            'marketplace',
            {
                'type': 'standard',
                'price': listing.price,
                'currency': listing.currency,
                'payment_id': payment_result['payment_id']
            },
            user_id
        )
        
        # Update listing status if needed
        if listing.asset.type == 'unique':
            listing.status = 'sold'
            
        db.session.add(purchase)
        db.session.commit()
        
        return {
            'purchase_id': purchase.id,
            'license_id': license.id,
            'download_url': listing.asset.file_url
        }
        
    def search_assets(
        self,
        query: str,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        tags: Optional[List[str]] = None,
        price_range: Optional[Dict] = None,
        sort_by: str = 'relevance',
        page: int = 1,
        per_page: int = 20
    ) -> Dict:
        """Search marketplace assets"""
        # Build base query
        base_query = Asset.query.join(AssetListing).filter(
            AssetListing.status == 'active'
        )
        
        # Apply filters
        if category:
            base_query = base_query.filter(Asset.category == category)
        if subcategory:
            base_query = base_query.filter(Asset.subcategory == subcategory)
        if tags:
            base_query = base_query.filter(Asset.tags.contains(tags))
        if price_range:
            if 'min' in price_range:
                base_query = base_query.filter(
                    AssetListing.price >= price_range['min']
                )
            if 'max' in price_range:
                base_query = base_query.filter(
                    AssetListing.price <= price_range['max']
                )
                
        # Apply sorting
        if sort_by == 'price_asc':
            base_query = base_query.order_by(AssetListing.price.asc())
        elif sort_by == 'price_desc':
            base_query = base_query.order_by(AssetListing.price.desc())
        elif sort_by == 'newest':
            base_query = base_query.order_by(Asset.created_at.desc())
        elif sort_by == 'rating':
            base_query = base_query.order_by(
                func.coalesce(Asset.average_rating, 0).desc()
            )
            
        # Paginate results
        paginated = base_query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return {
            'items': [item.to_dict() for item in paginated.items],
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page
        }
        
    def get_asset_details(self, asset_id: int) -> Dict:
        """Get detailed information about an asset"""
        asset = Asset.query.get(asset_id)
        if not asset:
            raise ValueError("Asset not found")
            
        # Get active listing if exists
        listing = AssetListing.query.filter_by(
            asset_id=asset_id,
            status='active'
        ).first()
        
        # Get reviews
        reviews = Review.query.filter_by(asset_id=asset_id).all()
        
        return {
            **asset.to_dict(),
            'listing': listing.to_dict() if listing else None,
            'reviews': [review.to_dict() for review in reviews]
        }
        
    def add_review(
        self,
        user_id: int,
        asset_id: int,
        rating: int,
        comment: Optional[str] = None
    ) -> Dict:
        """Add a review for an asset"""
        # Verify purchase
        purchase = Purchase.query.join(AssetListing).filter(
            Purchase.user_id == user_id,
            AssetListing.asset_id == asset_id
        ).first()
        
        if not purchase:
            raise ValueError("Must purchase asset before reviewing")
            
        # Create review
        review = Review(
            user_id=user_id,
            asset_id=asset_id,
            rating=rating,
            comment=comment
        )
        
        # Update asset rating
        asset = Asset.query.get(asset_id)
        asset.update_rating(rating)
        
        db.session.add(review)
        db.session.commit()
        
        return review.to_dict()
        
    def get_user_purchases(
        self,
        user_id: int,
        page: int = 1,
        per_page: int = 20
    ) -> Dict:
        """Get user's purchase history"""
        purchases = Purchase.query.filter_by(user_id=user_id).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return {
            'items': [purchase.to_dict() for purchase in purchases.items],
            'total': purchases.total,
            'pages': purchases.pages,
            'current_page': page
        }
        
    def get_user_sales(
        self,
        user_id: int,
        page: int = 1,
        per_page: int = 20
    ) -> Dict:
        """Get user's sales history"""
        sales = Purchase.query.join(AssetListing).join(Asset).filter(
            Asset.user_id == user_id
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return {
            'items': [sale.to_dict() for sale in sales.items],
            'total': sales.total,
            'pages': sales.pages,
            'current_page': page
        }
        
    def _process_payment(
        self,
        user_id: int,
        amount: float,
        currency: str,
        payment_info: Dict
    ) -> Dict:
        """Process payment for asset purchase"""
        # Implement payment processing logic
        commission = amount * self.marketplace_config['commission_rate']
        
        # In a real implementation, integrate with payment processor
        return {
            'payment_id': 'mock_payment_id',
            'status': 'success',
            'amount': amount,
            'commission': commission,
            'currency': currency
        }
