"""
Jira API integration service
"""
import requests
from typing import Dict, Any, Optional
from app.config import settings
from requests.auth import HTTPBasicAuth


class JiraService:
    """Service for integrating with Jira API"""
    
    def __init__(self, base_url: Optional[str] = None, email: Optional[str] = None, api_token: Optional[str] = None):
        self.base_url = base_url or settings.JIRA_BASE_URL
        self.email = email or settings.JIRA_EMAIL
        self.api_token = api_token or settings.JIRA_API_TOKEN
        
        if not all([self.base_url, self.email, self.api_token]):
            raise ValueError("Jira credentials not configured")
    
    def create_issue(
        self,
        summary: str,
        description: str,
        issue_type: str = "Task",
        project_key: str = None,
        priority: str = "Medium",
        assignee: Optional[str] = None,
        due_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a Jira issue
        
        Args:
            summary: Issue summary/title
            description: Issue description
            issue_type: Type of issue (Task, Bug, Story, etc.)
            project_key: Jira project key
            priority: Issue priority
            assignee: Jira user ID or email
            due_date: Due date in YYYY-MM-DD format
        
        Returns:
            Created issue data
        """
        if not project_key:
            raise ValueError("project_key is required")
        
        url = f"{self.base_url.rstrip('/')}/rest/api/3/issue"
        
        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": description}]
                        }
                    ]
                },
                "issuetype": {"name": issue_type},
                "priority": {"name": priority}
            }
        }
        
        if assignee:
            payload["fields"]["assignee"] = {"accountId": assignee}
        
        if due_date:
            payload["fields"]["duedate"] = due_date
        
        response = requests.post(
            url,
            json=payload,
            auth=HTTPBasicAuth(self.email, self.api_token),
            headers={"Accept": "application/json", "Content-Type": "application/json"}
        )
        
        response.raise_for_status()
        return response.json()
    
    def get_issue(self, issue_key: str) -> Dict[str, Any]:
        """Get issue details"""
        url = f"{self.base_url.rstrip('/')}/rest/api/3/issue/{issue_key}"
        
        response = requests.get(
            url,
            auth=HTTPBasicAuth(self.email, self.api_token),
            headers={"Accept": "application/json"}
        )
        
        response.raise_for_status()
        return response.json()
    
    def update_issue(self, issue_key: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing issue"""
        url = f"{self.base_url.rstrip('/')}/rest/api/3/issue/{issue_key}"
        
        payload = {"fields": updates}
        
        response = requests.put(
            url,
            json=payload,
            auth=HTTPBasicAuth(self.email, self.api_token),
            headers={"Accept": "application/json", "Content-Type": "application/json"}
        )
        
        response.raise_for_status()
        return response.json()


def get_jira_service_for_user(user_config: Dict[str, Any]) -> Optional[JiraService]:
    """Get Jira service instance for a specific user's configuration"""
    if not user_config.get("base_url") or not user_config.get("email") or not user_config.get("api_token"):
        return None
    
    return JiraService(
        base_url=user_config["base_url"],
        email=user_config["email"],
        api_token=user_config["api_token"]
    )

