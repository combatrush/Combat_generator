from typing import Dict, List, Optional
import asyncio
import json
from datetime import datetime
from websockets.server import WebSocketServerProtocol
from ..models.animation import Animation
from .. import db

class CollaborationSession:
    def __init__(self, project_id: int):
        self.project_id = project_id
        self.connected_users: Dict[int, WebSocketServerProtocol] = {}
        self.version_history: List[Dict] = []
        self.current_state: Dict = {}
        self.lock = asyncio.Lock()
    
    async def add_user(self, user_id: int, websocket: WebSocketServerProtocol):
        """Add user to collaboration session"""
        self.connected_users[user_id] = websocket
        await self.broadcast_message({
            'type': 'user_joined',
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def remove_user(self, user_id: int):
        """Remove user from collaboration session"""
        if user_id in self.connected_users:
            del self.connected_users[user_id]
            await self.broadcast_message({
                'type': 'user_left',
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat()
            })
    
    async def handle_edit(self, user_id: int, edit_data: Dict):
        """Handle edit from user"""
        async with self.lock:
            # Apply edit to current state
            self.apply_edit(edit_data)
            
            # Save version history
            self.version_history.append({
                'user_id': user_id,
                'edit_data': edit_data,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            # Broadcast edit to other users
            await self.broadcast_message({
                'type': 'edit',
                'user_id': user_id,
                'edit_data': edit_data,
                'timestamp': datetime.utcnow().isoformat()
            }, exclude_user=user_id)
    
    def apply_edit(self, edit_data: Dict):
        """Apply edit to current state"""
        # TODO: Implement edit application logic
        pass
    
    async def broadcast_message(self, message: Dict, exclude_user: Optional[int] = None):
        """Broadcast message to all connected users"""
        for user_id, websocket in self.connected_users.items():
            if exclude_user is not None and user_id == exclude_user:
                continue
            await websocket.send(json.dumps(message))

class CollaborationManager:
    def __init__(self):
        self.sessions: Dict[int, CollaborationSession] = {}
    
    def get_or_create_session(self, project_id: int) -> CollaborationSession:
        """Get existing session or create new one"""
        if project_id not in self.sessions:
            self.sessions[project_id] = CollaborationSession(project_id)
        return self.sessions[project_id]
    
    async def handle_connection(self, websocket: WebSocketServerProtocol, 
                              project_id: int, user_id: int):
        """Handle new WebSocket connection"""
        session = self.get_or_create_session(project_id)
        await session.add_user(user_id, websocket)
        
        try:
            async for message in websocket:
                data = json.loads(message)
                await session.handle_edit(user_id, data)
        finally:
            await session.remove_user(user_id)
            if not session.connected_users:
                del self.sessions[project_id]
    
    def get_version_history(self, project_id: int) -> List[Dict]:
        """Get version history for project"""
        if project_id in self.sessions:
            return self.sessions[project_id].version_history
        return []
