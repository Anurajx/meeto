"""
Trello API integration service
"""
import requests
from typing import Dict, Any, Optional, List
from app.config import settings


class TrelloService:
    """Service for integrating with Trello API"""
    
    def __init__(self, api_key: Optional[str] = None, api_token: Optional[str] = None, board_id: Optional[str] = None):
        self.api_key = api_key or settings.TRELLO_API_KEY
        self.api_token = api_token or settings.TRELLO_API_TOKEN
        self.board_id = board_id or settings.TRELLO_BOARD_ID
        self.base_url = "https://api.trello.com/1"
        
        if not all([self.api_key, self.api_token]):
            raise ValueError("Trello credentials not configured")
    
    def create_card(
        self,
        name: str,
        desc: str,
        list_id: Optional[str] = None,
        due_date: Optional[str] = None,
        labels: Optional[List[str]] = None,
        members: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a Trello card
        
        Args:
            name: Card name
            desc: Card description
            list_id: ID of the list to add card to
            due_date: Due date in ISO format (YYYY-MM-DDTHH:MM:SSZ)
            labels: List of label IDs
            members: List of member IDs
        
        Returns:
            Created card data
        """
        if not list_id:
            # Get first list from board
            lists = self.get_board_lists(self.board_id)
            if not lists:
                raise ValueError("No lists found in board")
            list_id = lists[0]["id"]
        
        url = f"{self.base_url}/cards"
        
        params = {
            "key": self.api_key,
            "token": self.api_token,
            "name": name,
            "desc": desc,
            "idList": list_id,
        }
        
        if due_date:
            params["due"] = due_date
        
        if labels:
            params["idLabels"] = ",".join(labels)
        
        if members:
            params["idMembers"] = ",".join(members)
        
        response = requests.post(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_board_lists(self, board_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all lists from a board"""
        board_id = board_id or self.board_id
        if not board_id:
            raise ValueError("board_id is required")
        
        url = f"{self.base_url}/boards/{board_id}/lists"
        
        params = {
            "key": self.api_key,
            "token": self.api_token
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_card(self, card_id: str) -> Dict[str, Any]:
        """Get card details"""
        url = f"{self.base_url}/cards/{card_id}"
        
        params = {
            "key": self.api_key,
            "token": self.api_token
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def update_card(self, card_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing card"""
        url = f"{self.base_url}/cards/{card_id}"
        
        params = {
            "key": self.api_key,
            "token": self.api_token,
            **updates
        }
        
        response = requests.put(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def delete_card(self, card_id: str) -> None:
        """Delete a card"""
        url = f"{self.base_url}/cards/{card_id}"
        
        params = {
            "key": self.api_key,
            "token": self.api_token
        }
        
        response = requests.delete(url, params=params)
        response.raise_for_status()


def get_trello_service_for_user(user_config: Dict[str, Any]) -> Optional[TrelloService]:
    """Get Trello service instance for a specific user's configuration"""
    if not user_config.get("api_key") or not user_config.get("api_token"):
        return None
    
    return TrelloService(
        api_key=user_config["api_key"],
        api_token=user_config["api_token"],
        board_id=user_config.get("board_id")
    )

