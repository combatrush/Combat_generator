from typing import Dict, List, Optional
from datetime import datetime, timedelta
import hashlib
import json
from ..models.license import License, LicenseTransaction
from .. import db

class LicenseManager:
    def __init__(self, config: Dict):
        """Initialize license management system"""
        self.config = config
        self.supported_licenses = {
            'creative_commons': {
                'cc0': {'attribution_required': False, 'commercial_use': True},
                'cc-by': {'attribution_required': True, 'commercial_use': True},
                'cc-by-sa': {'attribution_required': True, 'commercial_use': True},
                'cc-by-nc': {'attribution_required': True, 'commercial_use': False}
            },
            'commercial': {
                'standard': {'attribution_required': False, 'commercial_use': True},
                'extended': {'attribution_required': False, 'commercial_use': True},
                'enterprise': {'attribution_required': False, 'commercial_use': True}
            }
        }
        
    def acquire_license(
        self,
        asset_id: str,
        source: str,
        license_info: Dict,
        user_id: int
    ) -> Optional[License]:
        """Acquire new license for asset"""
        # Verify license compatibility
        if not self._verify_license_compatibility(license_info):
            return None
            
        # Create license record
        license = License(
            asset_id=asset_id,
            source=source,
            license_type=license_info['type'],
            terms=license_info.get('terms', {}),
            restrictions=license_info.get('restrictions', {}),
            attribution_required=self._check_attribution_required(license_info),
            commercial_use=self._check_commercial_use(license_info),
            source_url=license_info.get('source_url'),
            source_id=license_info.get('source_id')
        )
        
        # Set expiration if applicable
        if 'duration' in license_info:
            license.expires_at = datetime.utcnow() + timedelta(
                days=license_info['duration']
            )
            
        # Generate verification hash
        license.verification_hash = self._generate_verification_hash(license)
        license.verified_at = datetime.utcnow()
        
        # Create transaction record if paid license
        if license_info.get('price'):
            transaction = LicenseTransaction(
                license_id=license.id,
                user_id=user_id,
                transaction_type='purchase',
                amount=license_info['price'],
                currency=license_info.get('currency', 'USD'),
                payment_method=license_info.get('payment_method'),
                payment_id=license_info.get('payment_id')
            )
            db.session.add(transaction)
            
        db.session.add(license)
        db.session.commit()
        
        return license
        
    def verify_license(self, license_id: int) -> Dict:
        """Verify license validity"""
        license = License.query.get(license_id)
        if not license:
            return {'valid': False, 'reason': 'License not found'}
            
        # Check expiration
        if license.expires_at and license.expires_at < datetime.utcnow():
            return {'valid': False, 'reason': 'License expired'}
            
        # Verify hash
        current_hash = self._generate_verification_hash(license)
        if current_hash != license.verification_hash:
            return {'valid': False, 'reason': 'License verification failed'}
            
        return {
            'valid': True,
            'license': license.to_dict()
        }
        
    def get_attribution_requirements(self, license_id: int) -> Dict:
        """Get attribution requirements for license"""
        license = License.query.get(license_id)
        if not license:
            return {}
            
        if not license.attribution_required:
            return {'required': False}
            
        return {
            'required': True,
            'text': license.get_attribution_text(),
            'terms': license.terms.get('attribution_terms', {})
        }
        
    def _verify_license_compatibility(self, license_info: Dict) -> bool:
        """Verify if license is compatible with platform requirements"""
        license_type = license_info.get('type', '')
        category = license_info.get('category', 'commercial')
        
        if category not in self.supported_licenses:
            return False
            
        if license_type not in self.supported_licenses[category]:
            return False
            
        return True
        
    def _check_attribution_required(self, license_info: Dict) -> bool:
        """Check if license requires attribution"""
        category = license_info.get('category', 'commercial')
        license_type = license_info.get('type', '')
        
        if category in self.supported_licenses and license_type in self.supported_licenses[category]:
            return self.supported_licenses[category][license_type]['attribution_required']
            
        return True  # Default to requiring attribution
        
    def _check_commercial_use(self, license_info: Dict) -> bool:
        """Check if license allows commercial use"""
        category = license_info.get('category', 'commercial')
        license_type = license_info.get('type', '')
        
        if category in self.supported_licenses and license_type in self.supported_licenses[category]:
            return self.supported_licenses[category][license_type]['commercial_use']
            
        return False  # Default to no commercial use
        
    def _generate_verification_hash(self, license: License) -> str:
        """Generate verification hash for license"""
        data = {
            'asset_id': license.asset_id,
            'source': license.source,
            'license_type': license.license_type,
            'terms': license.terms,
            'restrictions': license.restrictions,
            'source_url': license.source_url,
            'source_id': license.source_id
        }
        
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
