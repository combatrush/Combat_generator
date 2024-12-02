from typing import Dict, List, Optional, Union
import os
import json
import hashlib
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..models.asset import Asset

class AssetManager:
    def __init__(self, config: Dict):
        """Initialize asset management system"""
        self.config = config
        self.storage_path = config['ASSET_LIBRARY_PATH']
        self._init_storage()
        self._init_database()
        
    def _init_storage(self):
        """Initialize storage directories"""
        # Create main directories
        for category in ['characters', 'effects', 'sounds', 'environments', 'props']:
            path = os.path.join(self.storage_path, category)
            os.makedirs(path, exist_ok=True)
            
    def _init_database(self):
        """Initialize database connection"""
        self.engine = create_engine(self.config['SQLALCHEMY_DATABASE_URI'])
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
    def store_asset(
        self,
        asset_data: Dict,
        category: str,
        metadata: Dict,
        user_id: int
    ) -> Asset:
        """Store new asset in the system"""
        # Generate unique asset ID
        asset_id = self._generate_asset_id(asset_data)
        
        # Store asset files
        storage_info = self._store_asset_files(asset_data, category, asset_id)
        
        # Create asset record
        asset = Asset(
            id=asset_id,
            name=metadata.get('name', 'Unnamed Asset'),
            type=category,
            category=metadata.get('subcategory', 'general'),
            project_id=metadata.get('project_id'),
            data=storage_info,
            metadata=metadata,
            settings=metadata.get('settings', {}),
            storage_path=storage_info['base_path'],
            file_size=storage_info['total_size']
        )
        
        # Save to database
        self.session.add(asset)
        self.session.commit()
        
        return asset
        
    def _generate_asset_id(self, asset_data: Dict) -> str:
        """Generate unique asset ID"""
        timestamp = datetime.utcnow().isoformat()
        data_str = json.dumps(asset_data, sort_keys=True)
        return hashlib.sha256(f"{timestamp}{data_str}".encode()).hexdigest()[:16]
        
    def _store_asset_files(
        self,
        asset_data: Dict,
        category: str,
        asset_id: str
    ) -> Dict:
        """Store asset files in appropriate location"""
        base_path = os.path.join(self.storage_path, category, asset_id)
        os.makedirs(base_path, exist_ok=True)
        
        storage_info = {
            'base_path': base_path,
            'files': {},
            'total_size': 0
        }
        
        # Store different asset components
        for component, data in asset_data.items():
            file_info = self._store_component(base_path, component, data)
            storage_info['files'][component] = file_info
            storage_info['total_size'] += file_info['size']
            
        return storage_info
        
    def _store_component(
        self,
        base_path: str,
        component: str,
        data: Union[bytes, Dict]
    ) -> Dict:
        """Store individual asset component"""
        file_path = os.path.join(base_path, f"{component}")
        
        if isinstance(data, bytes):
            # Store binary data
            with open(file_path, 'wb') as f:
                f.write(data)
        else:
            # Store JSON data
            with open(f"{file_path}.json", 'w') as f:
                json.dump(data, f)
            file_path = f"{file_path}.json"
            
        return {
            'path': file_path,
            'size': os.path.getsize(file_path)
        }
        
    def get_asset(self, asset_id: str) -> Optional[Asset]:
        """Retrieve asset by ID"""
        return self.session.query(Asset).filter(Asset.id == asset_id).first()
        
    def search_assets(
        self,
        category: Optional[str] = None,
        query: Optional[str] = None,
        filters: Optional[Dict] = None
    ) -> List[Asset]:
        """Search assets with filters"""
        query = self.session.query(Asset)
        
        if category:
            query = query.filter(Asset.type == category)
            
        if filters:
            for key, value in filters.items():
                if key in Asset.__table__.columns:
                    query = query.filter(getattr(Asset, key) == value)
                    
        return query.all()
        
    def update_asset(
        self,
        asset_id: str,
        updates: Dict
    ) -> Optional[Asset]:
        """Update asset metadata or settings"""
        asset = self.get_asset(asset_id)
        if not asset:
            return None
            
        # Update fields
        for key, value in updates.items():
            if hasattr(asset, key):
                setattr(asset, key, value)
                
        self.session.commit()
        return asset
        
    def delete_asset(self, asset_id: str) -> bool:
        """Delete asset and its files"""
        asset = self.get_asset(asset_id)
        if not asset:
            return False
            
        # Delete files
        if os.path.exists(asset.storage_path):
            for root, dirs, files in os.walk(asset.storage_path, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(asset.storage_path)
            
        # Delete database record
        self.session.delete(asset)
        self.session.commit()
        
        return True
