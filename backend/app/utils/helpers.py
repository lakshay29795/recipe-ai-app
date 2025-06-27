"""
Helper utilities for common operations
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import re


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix"""
    unique_id = str(uuid.uuid4())
    return f"{prefix}_{unique_id}" if prefix else unique_id


def sanitize_string(text: str) -> str:
    """Sanitize string input by removing special characters"""
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text.strip()


def format_cooking_time(minutes: int) -> str:
    """Format cooking time in minutes to human-readable format"""
    if minutes < 60:
        return f"{minutes} minutes"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    if remaining_minutes == 0:
        return f"{hours} hour{'s' if hours > 1 else ''}"
    
    return f"{hours} hour{'s' if hours > 1 else ''} {remaining_minutes} minutes"


def serialize_datetime(dt: datetime) -> str:
    """Serialize datetime to ISO string"""
    if isinstance(dt, datetime):
        return dt.isoformat()
    return dt


def deserialize_datetime(dt_str: str) -> Optional[datetime]:
    """Deserialize ISO string to datetime"""
    try:
        if isinstance(dt_str, str):
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt_str
    except (ValueError, AttributeError):
        return None


def clean_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove None values from dictionary"""
    return {k: v for k, v in data.items() if v is not None}


def normalize_ingredient_name(name: str) -> str:
    """Normalize ingredient name for consistency"""
    if not name:
        return ""
    
    # Convert to lowercase and strip whitespace
    normalized = name.lower().strip()
    
    # Remove extra spaces
    normalized = ' '.join(normalized.split())
    
    # Remove common prefixes/suffixes
    common_removals = [
        "fresh ", "dried ", "ground ", "whole ", "chopped ", "diced ",
        "sliced ", "minced ", "organic ", "raw "
    ]
    
    for removal in common_removals:
        if normalized.startswith(removal):
            normalized = normalized[len(removal):]
    
    return normalized


def parse_ingredient_quantity(text: str) -> Dict[str, Any]:
    """Parse ingredient text to extract quantity, unit, and name"""
    # Simple regex patterns for common formats
    patterns = [
        r'^(\d+(?:\.\d+)?)\s*([a-zA-Z]+)\s+(.+)$',  # "2 cups flour"
        r'^(\d+(?:\.\d+)?)\s+(.+)$',  # "2 eggs"
        r'^(.+)$'  # "salt to taste"
    ]
    
    for pattern in patterns:
        match = re.match(pattern, text.strip())
        if match:
            groups = match.groups()
            if len(groups) == 3:
                return {
                    "amount": float(groups[0]),
                    "unit": groups[1],
                    "name": normalize_ingredient_name(groups[2])
                }
            elif len(groups) == 2:
                return {
                    "amount": float(groups[0]),
                    "unit": "piece",
                    "name": normalize_ingredient_name(groups[1])
                }
            else:
                return {
                    "amount": None,
                    "unit": None,
                    "name": normalize_ingredient_name(groups[0])
                }
    
    return {
        "amount": None,
        "unit": None,
        "name": normalize_ingredient_name(text)
    }


def calculate_recipe_difficulty(
    ingredients_count: int,
    instructions_count: int,
    cooking_time: int,
    techniques: List[str] = None
) -> str:
    """Calculate recipe difficulty based on various factors"""
    score = 0
    
    # Ingredients complexity
    if ingredients_count <= 5:
        score += 1
    elif ingredients_count <= 10:
        score += 2
    else:
        score += 3
    
    # Instructions complexity
    if instructions_count <= 3:
        score += 1
    elif instructions_count <= 6:
        score += 2
    else:
        score += 3
    
    # Cooking time
    if cooking_time <= 30:
        score += 1
    elif cooking_time <= 60:
        score += 2
    else:
        score += 3
    
    # Advanced techniques
    if techniques:
        advanced_techniques = [
            "braise", "flambe", "sous vide", "ferment", "cure", "smoke"
        ]
        if any(tech.lower() in ' '.join(techniques).lower() for tech in advanced_techniques):
            score += 2
    
    # Determine difficulty
    if score <= 4:
        return "easy"
    elif score <= 7:
        return "medium"
    else:
        return "hard"


def paginate_results(
    items: List[Any],
    page: int,
    limit: int
) -> Dict[str, Any]:
    """Paginate a list of items"""
    total = len(items)
    start_index = (page - 1) * limit
    end_index = start_index + limit
    
    paginated_items = items[start_index:end_index]
    
    return {
        "items": paginated_items,
        "total": total,
        "page": page,
        "limit": limit,
        "has_next": end_index < total,
        "has_prev": page > 1
    } 