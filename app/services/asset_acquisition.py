import requests
import os
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
import json
import hashlib
from datetime import datetime
from urllib.parse import urljoin

@dataclass
class AssetSource:
    name: str
    base_url: str
    api_key: str
    license_type: str
    asset_types: List[str]
    rate_limit: Dict[str, int]

class AssetAcquisitionService:
    def __init__(self, config: Dict):
        """Initialize asset acquisition service"""
        self.config = config
        self.sources = self._init_sources()
        self.cache_dir = os.path.join(config['ASSET_LIBRARY_PATH'], '_cache')
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def _init_sources(self) -> Dict[str, AssetSource]:
        """Initialize asset sources with API credentials"""
        sources = {
            'mixamo': AssetSource(
                name='Mixamo',
                base_url='https://www.mixamo.com/api/',
                api_key=os.getenv('MIXAMO_API_KEY', ''),
                license_type='adobe_creative_cloud',
                asset_types=['character', 'animation'],
                rate_limit={'requests_per_minute': 60}
            ),
            'sketchfab': AssetSource(
                name='Sketchfab',
                base_url='https://api.sketchfab.com/v3/',
                api_key=os.getenv('SKETCHFAB_API_KEY', ''),
                license_type='sketchfab_standard',
                asset_types=['character', 'prop', 'environment'],
                rate_limit={'requests_per_minute': 100}
            ),
            'freesound': AssetSource(
                name='Freesound',
                base_url='https://freesound.org/apiv2/',
                api_key=os.getenv('FREESOUND_API_KEY', ''),
                license_type='creative_commons',
                asset_types=['sound'],
                rate_limit={'requests_per_minute': 60}
            ),
            'turbosquid': AssetSource(
                name='TurboSquid',
                base_url='https://api.turbosquid.com/v1/',
                api_key=os.getenv('TURBOSQUID_API_KEY', ''),
                license_type='turbosquid_standard',
                asset_types=['character', 'prop', 'environment'],
                rate_limit={'requests_per_minute': 100}
            )
        }
        return sources

    def search_assets(
        self,
        query: str,
        asset_type: str,
        source: Optional[str] = None,
        license_type: Optional[str] = None,
        max_results: int = 50
    ) -> List[Dict]:
        """Search for assets across specified sources"""
        results = []
        
        # Determine which sources to search
        search_sources = (
            [self.sources[source]] if source
            else [s for s in self.sources.values() if asset_type in s.asset_types]
        )
        
        for src in search_sources:
            if license_type and src.license_type != license_type:
                continue
                
            source_results = self._search_source(
                src, query, asset_type, max_results
            )
            results.extend(source_results)
            
        return results[:max_results]
    
    def _search_source(
        self,
        source: AssetSource,
        query: str,
        asset_type: str,
        max_results: int
    ) -> List[Dict]:
        """Search specific source for assets"""
        if source.name == 'Mixamo':
            return self._search_mixamo(query, asset_type, max_results)
        elif source.name == 'Sketchfab':
            return self._search_sketchfab(query, asset_type, max_results)
        elif source.name == 'Freesound':
            return self._search_freesound(query, max_results)
        elif source.name == 'TurboSquid':
            return self._search_turbosquid(query, asset_type, max_results)
        return []

    def download_asset(
        self,
        asset_info: Dict,
        source: str,
        target_dir: str
    ) -> Optional[str]:
        """Download asset from source"""
        source_obj = self.sources.get(source)
        if not source_obj:
            return None
            
        # Create cache key for asset
        cache_key = self._generate_cache_key(asset_info)
        cache_path = os.path.join(self.cache_dir, cache_key)
        
        # Check cache first
        if os.path.exists(cache_path):
            return self._process_cached_asset(cache_path, target_dir)
            
        # Download based on source
        if source == 'mixamo':
            return self._download_mixamo_asset(asset_info, cache_path, target_dir)
        elif source == 'sketchfab':
            return self._download_sketchfab_asset(asset_info, cache_path, target_dir)
        elif source == 'freesound':
            return self._download_freesound_asset(asset_info, cache_path, target_dir)
        elif source == 'turbosquid':
            return self._download_turbosquid_asset(asset_info, cache_path, target_dir)
            
        return None

    def verify_license(self, asset_info: Dict, source: str) -> Dict:
        """Verify and retrieve license information for asset"""
        source_obj = self.sources.get(source)
        if not source_obj:
            return {'valid': False, 'reason': 'Invalid source'}
            
        # Check license type compatibility
        if source == 'mixamo':
            return self._verify_mixamo_license(asset_info)
        elif source == 'sketchfab':
            return self._verify_sketchfab_license(asset_info)
        elif source == 'freesound':
            return self._verify_freesound_license(asset_info)
        elif source == 'turbosquid':
            return self._verify_turbosquid_license(asset_info)
            
        return {'valid': False, 'reason': 'Unknown source'}

    def _generate_cache_key(self, asset_info: Dict) -> str:
        """Generate unique cache key for asset"""
        data_str = json.dumps(asset_info, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    # Source-specific implementations
    def _search_mixamo(self, query: str, asset_type: str, max_results: int) -> List[Dict]:
        """Search Mixamo for assets"""
        # TODO: Implement Mixamo API search
        # This would require Adobe Creative Cloud authentication
        return []

    def _search_sketchfab(self, query: str, asset_type: str, max_results: int) -> List[Dict]:
        """Search Sketchfab for assets"""
        source = self.sources['sketchfab']
        headers = {'Authorization': f'Bearer {source.api_key}'}
        
        params = {
            'q': query,
            'type': asset_type,
            'downloadable': True,
            'count': max_results
        }
        
        response = requests.get(
            urljoin(source.base_url, 'search'),
            headers=headers,
            params=params
        )
        
        if response.status_code == 200:
            data = response.json()
            return [
                {
                    'id': item['uid'],
                    'title': item['name'],
                    'thumbnail_url': item['thumbnails']['images'][0]['url'],
                    'download_url': item['download_url'],
                    'license': item['license'],
                    'source': 'sketchfab'
                }
                for item in data['results']
            ]
        return []

    def _search_freesound(self, query: str, max_results: int) -> List[Dict]:
        """Search Freesound for audio assets"""
        source = self.sources['freesound']
        params = {
            'query': query,
            'token': source.api_key,
            'page_size': max_results,
            'fields': 'id,name,previews,download,license'
        }
        
        response = requests.get(
            urljoin(source.base_url, 'search/text/'),
            params=params
        )
        
        if response.status_code == 200:
            data = response.json()
            return [
                {
                    'id': item['id'],
                    'title': item['name'],
                    'preview_url': item['previews']['preview-hq-mp3'],
                    'download_url': item['download'],
                    'license': item['license'],
                    'source': 'freesound'
                }
                for item in data['results']
            ]
        return []

    def _search_turbosquid(self, query: str, asset_type: str, max_results: int) -> List[Dict]:
        """Search TurboSquid for 3D assets"""
        # TODO: Implement TurboSquid API search
        return []

    def _verify_license(self, asset_info: Dict, source: str) -> bool:
        """Verify license compatibility"""
        source_obj = self.sources.get(source)
        if not source_obj:
            return False
            
        # Check license type and restrictions
        license_info = asset_info.get('license', {})
        
        # Basic license compatibility check
        if source_obj.license_type == 'creative_commons':
            return self._verify_cc_license(license_info)
        elif source_obj.license_type in ['adobe_creative_cloud', 'turbosquid_standard']:
            return self._verify_commercial_license(license_info)
            
        return False

    def _verify_cc_license(self, license_info: Dict) -> bool:
        """Verify Creative Commons license compatibility"""
        allowed_licenses = ['cc0', 'cc-by', 'cc-by-sa']
        return license_info.get('type', '').lower() in allowed_licenses

    def _verify_commercial_license(self, license_info: Dict) -> bool:
        """Verify commercial license compatibility"""
        return license_info.get('commercial_use', False)
