"""
Input validation utilities
"""

from typing import List, Dict, Any, Optional
import re
from email_validator import validate_email, EmailNotValidError


def is_valid_email(email: str) -> bool:
    """Validate email address format"""
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False


def is_valid_password(password: str) -> bool:
    """Validate password strength"""
    if len(password) < 8:
        return False
    
    # Check for at least one uppercase, lowercase, and digit
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    return has_upper and has_lower and has_digit


def sanitize_ingredient_list(ingredients: List[str]) -> List[str]:
    """Sanitize and validate ingredient list"""
    cleaned_ingredients = []
    
    for ingredient in ingredients:
        if isinstance(ingredient, str):
            # Remove extra whitespace and empty strings
            cleaned = ingredient.strip()
            if cleaned and len(cleaned) > 0:
                # Remove any potential injection attempts
                cleaned = re.sub(r'[<>"\']', '', cleaned)
                if len(cleaned) <= 200:  # Reasonable length limit
                    cleaned_ingredients.append(cleaned)
    
    return cleaned_ingredients


def validate_recipe_data(recipe_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Validate recipe data and return validation errors"""
    errors = {}
    
    # Required fields
    required_fields = ['title', 'description', 'ingredients', 'instructions']
    for field in required_fields:
        if field not in recipe_data or not recipe_data[field]:
            errors[field] = ['This field is required']
    
    # Title validation
    if 'title' in recipe_data:
        title = recipe_data['title']
        if len(title) < 3:
            errors.setdefault('title', []).append('Title must be at least 3 characters long')
        elif len(title) > 200:
            errors.setdefault('title', []).append('Title must be less than 200 characters')
    
    # Description validation
    if 'description' in recipe_data:
        description = recipe_data['description']
        if len(description) < 10:
            errors.setdefault('description', []).append('Description must be at least 10 characters long')
        elif len(description) > 1000:
            errors.setdefault('description', []).append('Description must be less than 1000 characters')
    
    # Ingredients validation
    if 'ingredients' in recipe_data:
        ingredients = recipe_data['ingredients']
        if not isinstance(ingredients, list):
            errors.setdefault('ingredients', []).append('Ingredients must be a list')
        elif len(ingredients) == 0:
            errors.setdefault('ingredients', []).append('At least one ingredient is required')
        elif len(ingredients) > 50:
            errors.setdefault('ingredients', []).append('Maximum 50 ingredients allowed')
    
    # Instructions validation
    if 'instructions' in recipe_data:
        instructions = recipe_data['instructions']
        if not isinstance(instructions, list):
            errors.setdefault('instructions', []).append('Instructions must be a list')
        elif len(instructions) == 0:
            errors.setdefault('instructions', []).append('At least one instruction is required')
        elif len(instructions) > 20:
            errors.setdefault('instructions', []).append('Maximum 20 instructions allowed')
    
    # Cooking time validation
    if 'cooking_time' in recipe_data:
        cooking_time = recipe_data['cooking_time']
        if not isinstance(cooking_time, int) or cooking_time < 0:
            errors.setdefault('cooking_time', []).append('Cooking time must be a positive number')
        elif cooking_time > 1440:  # 24 hours in minutes
            errors.setdefault('cooking_time', []).append('Cooking time cannot exceed 24 hours')
    
    # Servings validation
    if 'servings' in recipe_data:
        servings = recipe_data['servings']
        if not isinstance(servings, int) or servings < 1:
            errors.setdefault('servings', []).append('Servings must be at least 1')
        elif servings > 100:
            errors.setdefault('servings', []).append('Maximum 100 servings allowed')
    
    return errors


def validate_user_preferences(preferences: Dict[str, Any]) -> Dict[str, List[str]]:
    """Validate user preferences data"""
    errors = {}
    
    # Dietary restrictions
    if 'dietary_restrictions' in preferences:
        restrictions = preferences['dietary_restrictions']
        if not isinstance(restrictions, list):
            errors.setdefault('dietary_restrictions', []).append('Must be a list')
        else:
            valid_restrictions = [
                'vegetarian', 'vegan', 'gluten-free', 'dairy-free', 'keto',
                'paleo', 'low-carb', 'low-fat', 'halal', 'kosher'
            ]
            for restriction in restrictions:
                if restriction not in valid_restrictions:
                    errors.setdefault('dietary_restrictions', []).append(f'Invalid dietary restriction: {restriction}')
    
    # Allergies
    if 'allergies' in preferences:
        allergies = preferences['allergies']
        if not isinstance(allergies, list):
            errors.setdefault('allergies', []).append('Must be a list')
        elif len(allergies) > 20:
            errors.setdefault('allergies', []).append('Maximum 20 allergies allowed')
    
    # Cooking skill level
    if 'cooking_skill_level' in preferences:
        skill_level = preferences['cooking_skill_level']
        valid_levels = ['beginner', 'intermediate', 'advanced', 'expert']
        if skill_level not in valid_levels:
            errors.setdefault('cooking_skill_level', []).append('Invalid skill level')
    
    # Spice level
    if 'spice_level' in preferences:
        spice_level = preferences['spice_level']
        valid_levels = ['none', 'mild', 'medium', 'hot', 'extra-hot']
        if spice_level not in valid_levels:
            errors.setdefault('spice_level', []).append('Invalid spice level')
    
    return errors


def is_safe_filename(filename: str) -> bool:
    """Check if filename is safe for storage"""
    # Remove any path separators
    safe_filename = filename.replace('/', '').replace('\\', '')
    
    # Check for reasonable length
    if len(safe_filename) > 255:
        return False
    
    # Check for valid characters (alphanumeric, dots, hyphens, underscores)
    if not re.match(r'^[a-zA-Z0-9._-]+$', safe_filename):
        return False
    
    # Avoid reserved names
    reserved_names = ['CON', 'PRN', 'AUX', 'NUL'] + [f'COM{i}' for i in range(1, 10)] + [f'LPT{i}' for i in range(1, 10)]
    if safe_filename.upper() in reserved_names:
        return False
    
    return True


def validate_search_query(query: str) -> Optional[str]:
    """Validate and sanitize search query"""
    if not query or not isinstance(query, str):
        return None
    
    # Remove extra whitespace
    cleaned_query = ' '.join(query.split())
    
    # Check length
    if len(cleaned_query) < 2:
        return None
    elif len(cleaned_query) > 100:
        cleaned_query = cleaned_query[:100]
    
    # Remove potentially harmful characters
    cleaned_query = re.sub(r'[<>"\']', '', cleaned_query)
    
    return cleaned_query if cleaned_query else None 