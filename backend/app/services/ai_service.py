"""
AI service for recipe generation using OpenAI API
"""

import openai
from typing import Dict, List, Optional, Any
import json
import structlog
from app.core.config import settings
from app.models.recipe_models import Recipe, RecipeIngredient, RecipeStep
from app.models.common_models import DietaryRestriction, Difficulty, SkillLevel
import asyncio
import httpx
from datetime import datetime

logger = structlog.get_logger(__name__)


class AIService:
    """AI service for recipe generation and image creation"""
    
    def __init__(self):
        self.client = None
        self._initialize_openai()
    
    def _initialize_openai(self):
        """Initialize OpenAI client"""
        try:
            if not settings.OPENAI_API_KEY:
                logger.warning("OpenAI API key not configured")
                return
            
            self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize OpenAI client", error=str(e))
    
    async def generate_recipe(
        self,
        ingredients: List[str],
        dietary_restrictions: Optional[List[DietaryRestriction]] = None,
        cuisine_preference: Optional[str] = None,
        difficulty: Optional[Difficulty] = None,
        max_cooking_time: Optional[int] = None,
        servings: int = 4,
        additional_notes: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Generate a recipe using OpenAI GPT-4"""
        if not self.client:
            logger.error("OpenAI client not initialized")
            return None
        
        try:
            # Build the prompt
            prompt = self._build_recipe_prompt(
                ingredients=ingredients,
                dietary_restrictions=dietary_restrictions,
                cuisine_preference=cuisine_preference,
                difficulty=difficulty,
                max_cooking_time=max_cooking_time,
                servings=servings,
                additional_notes=additional_notes
            )
            
            # Generate recipe using GPT-4
            response = await asyncio.to_thread(
                self._call_openai_chat,
                prompt
            )
            
            if not response:
                return None
            
            # Parse the response
            recipe_data = self._parse_recipe_response(response)
            
            if recipe_data:
                # Validate and enhance the recipe
                recipe_data = self._validate_and_enhance_recipe(recipe_data)
                logger.info("Recipe generated successfully", recipe_title=recipe_data.get('title'))
                return recipe_data
            
            return None
            
        except Exception as e:
            logger.error("Failed to generate recipe", error=str(e))
            return None
    
    def _call_openai_chat(self, prompt: str) -> Optional[str]:
        """Make synchronous call to OpenAI Chat API"""
        try:
            # Try with JSON mode first, fallback if not supported
            try:
                response = self.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional chef and cookbook writer. Generate detailed, practical recipes in JSON format. Always provide exact measurements, clear instructions, and helpful cooking tips. Respond with valid JSON only."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=settings.OPENAI_MAX_TOKENS,
                    temperature=settings.OPENAI_TEMPERATURE,
                    response_format={"type": "json_object"}
                )
            except Exception as e:
                # Fallback without response_format for older models
                logger.warning("JSON mode not supported, falling back to regular mode", error=str(e))
                response = self.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional chef and cookbook writer. Generate detailed, practical recipes in JSON format. Always provide exact measurements, clear instructions, and helpful cooking tips. IMPORTANT: Respond with valid JSON only, no additional text."
                        },
                        {
                            "role": "user",
                            "content": prompt + "\n\nIMPORTANT: Return only valid JSON, no other text or formatting."
                        }
                    ],
                    max_tokens=settings.OPENAI_MAX_TOKENS,
                    temperature=settings.OPENAI_TEMPERATURE
                )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error("OpenAI API call failed", error=str(e))
            return None
    
    def _build_recipe_prompt(
        self,
        ingredients: List[str],
        dietary_restrictions: Optional[List[DietaryRestriction]] = None,
        cuisine_preference: Optional[str] = None,
        difficulty: Optional[Difficulty] = None,
        max_cooking_time: Optional[int] = None,
        servings: int = 4,
        additional_notes: Optional[str] = None
    ) -> str:
        """Build comprehensive prompt for recipe generation"""
        
        prompt = f"""Create a detailed recipe using these ingredients: {', '.join(ingredients)}

REQUIREMENTS:
- Servings: {servings}
- Format: Valid JSON object with the exact structure below"""
        
        if dietary_restrictions:
            restrictions = [r.value if hasattr(r, 'value') else str(r) for r in dietary_restrictions]
            prompt += f"\n- Dietary restrictions: {', '.join(restrictions)}"
        
        if cuisine_preference:
            prompt += f"\n- Cuisine style: {cuisine_preference}"
        
        if difficulty:
            difficulty_str = difficulty.value if hasattr(difficulty, 'value') else str(difficulty)
            prompt += f"\n- Difficulty level: {difficulty_str}"
        
        if max_cooking_time:
            prompt += f"\n- Maximum cooking time: {max_cooking_time} minutes"
        
        if additional_notes:
            prompt += f"\n- Additional notes: {additional_notes}"
        
        prompt += """

JSON STRUCTURE (respond with this exact format):
{
  "title": "Recipe Name",
  "description": "Brief description of the dish",
  "cuisine": "cuisine type",
  "difficulty": "easy|medium|hard",
  "prep_time": 15,
  "cooking_time": 30,
  "total_time": 45,
  "servings": 4,
  "ingredients": [
    {
      "name": "ingredient name",
      "amount": 2,
      "unit": "cups",
      "notes": "optional preparation notes"
    }
  ],
     "instructions": [
     {
       "step_number": 1,
       "instruction": "Detailed step-by-step instruction",
       "duration": 5,
       "temperature": 180
     }
   ],
  "nutrition": {
    "calories": 350,
    "protein": 25,
    "carbs": 30,
    "fat": 12,
    "fiber": 8
  },
  "tags": ["quick", "healthy", "one-pot"],
  "tips": [
    "Helpful cooking tip or variation"
  ],
  "substitutions": [
    {
      "original": "ingredient name",
      "substitute": "substitute ingredient",
      "ratio": "1:1",
      "notes": "substitution notes"
    }
  ]
}

Generate a creative, practical recipe that uses the provided ingredients effectively."""
        
        return prompt
    
    def _parse_recipe_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse and validate OpenAI recipe response"""
        try:
            # Clean up the response
            response = response.strip()
            
            # Parse JSON
            recipe_data = json.loads(response)
            
            # Validate required fields
            required_fields = ['title', 'description', 'ingredients', 'instructions']
            for field in required_fields:
                if field not in recipe_data:
                    logger.error(f"Missing required field: {field}")
                    return None
            
            return recipe_data
            
        except json.JSONDecodeError as e:
            logger.error("Failed to parse recipe JSON", error=str(e))
            return None
        except Exception as e:
            logger.error("Failed to parse recipe response", error=str(e))
            return None
    
    def _validate_and_enhance_recipe(self, recipe_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance recipe data"""
        try:
            # Add missing fields with defaults
            recipe_data.setdefault('prep_time', 15)
            recipe_data.setdefault('cooking_time', 30)
            recipe_data.setdefault('total_time', recipe_data.get('prep_time', 15) + recipe_data.get('cooking_time', 30))
            recipe_data.setdefault('servings', 4)
            recipe_data.setdefault('difficulty', 'medium')
            recipe_data.setdefault('cuisine', 'international')
            recipe_data.setdefault('tags', [])
            recipe_data.setdefault('tips', [])
            recipe_data.setdefault('substitutions', [])
            
            # Add metadata
            recipe_data['id'] = f"recipe_{int(datetime.utcnow().timestamp())}"
            recipe_data['created_at'] = datetime.utcnow().isoformat()
            recipe_data['source'] = 'ai_generated'
            
            # Validate ingredients format
            if 'ingredients' in recipe_data:
                for i, ingredient in enumerate(recipe_data['ingredients']):
                    if isinstance(ingredient, str):
                        # Convert string to proper format
                        recipe_data['ingredients'][i] = {
                            'name': ingredient,
                            'amount': 1,
                            'unit': 'piece',
                            'notes': ''
                        }
                    else:
                        # Ensure required fields
                        ingredient.setdefault('amount', 1)
                        ingredient.setdefault('unit', 'piece')
                        ingredient.setdefault('notes', '')
            
            # Validate instructions format
            if 'instructions' in recipe_data:
                for i, instruction in enumerate(recipe_data['instructions']):
                    if isinstance(instruction, str):
                        # Convert string to proper format
                        recipe_data['instructions'][i] = {
                            'step_number': i + 1,
                            'instruction': instruction,
                            'duration': None,
                            'temperature': None
                        }
                    else:
                        # Ensure required fields
                        instruction.setdefault('step_number', i + 1)
                        instruction.setdefault('duration', instruction.pop('time', None))
                        
                        # Fix temperature field - convert string to int or None
                        temp = instruction.get('temperature')
                        if temp:
                            if isinstance(temp, str):
                                # Convert string temperatures to integers or None
                                temp_lower = temp.lower()
                                if 'low' in temp_lower:
                                    instruction['temperature'] = 150
                                elif 'medium' in temp_lower:
                                    instruction['temperature'] = 180
                                elif 'high' in temp_lower:
                                    instruction['temperature'] = 220
                                elif temp_lower in ['none', 'no', 'room']:
                                    instruction['temperature'] = None
                                else:
                                    # Try to parse as number
                                    try:
                                        instruction['temperature'] = int(float(temp))
                                    except ValueError:
                                        instruction['temperature'] = None
                            elif not isinstance(temp, int):
                                instruction['temperature'] = None
                        else:
                            instruction['temperature'] = None
            
            # Validate substitutions format
            if 'substitutions' in recipe_data:
                for i, substitution in enumerate(recipe_data['substitutions']):
                    if isinstance(substitution, dict):
                        # Fix alternatives format if present
                        if 'alternatives' in substitution and 'substitute' not in substitution:
                            alternatives = substitution.get('alternatives', [])
                            if alternatives and isinstance(alternatives, list):
                                # Use first alternative as substitute
                                substitution['substitute'] = alternatives[0]
                                # Add other alternatives to notes if multiple
                                if len(alternatives) > 1:
                                    other_alts = ', '.join(alternatives[1:])
                                    existing_notes = substitution.get('notes', '')
                                    substitution['notes'] = f"{existing_notes}. Other alternatives: {other_alts}".strip('. ')
                                # Remove alternatives field
                                del substitution['alternatives']
                        
                        # Ensure required fields
                        substitution.setdefault('substitute', 'substitute ingredient')
                        substitution.setdefault('ratio', '1:1')
                        substitution.setdefault('notes', '')
            
            return recipe_data
            
        except Exception as e:
            logger.error("Failed to validate recipe data", error=str(e))
            return recipe_data
    
    async def generate_recipe_image(
        self,
        recipe_title: str,
        cuisine: Optional[str] = None,
        ingredients: Optional[List[str]] = None
    ) -> Optional[str]:
        """Generate recipe image using DALL-E"""
        # Commented out for testing - using hardcoded image URL instead
        # if not self.client:
        #     logger.error("OpenAI client not initialized")
        #     return None
        
        try:
            # TODO: Uncomment for production use
            # Build image prompt
            # prompt = self._build_image_prompt(recipe_title, cuisine, ingredients)
            
            # Generate image using DALL-E
            # response = await asyncio.to_thread(
            #     self._call_openai_image,
            #     prompt
            # )
            
            # if response and response.data:
            #     image_url = response.data[0].url
            #     logger.info("Recipe image generated successfully", recipe_title=recipe_title)
            #     return image_url
            
            # For testing: return a hardcoded beautiful food image URL
            hardcoded_image_urls = [
                "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=800&h=600&fit=crop&crop=center",  # Pizza
                "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800&h=600&fit=crop&crop=center",  # Salad
                "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=800&h=600&fit=crop&crop=center",  # Pancakes
                "https://images.unsplash.com/photo-1565958011703-44f9829ba187?w=800&h=600&fit=crop&crop=center",  # Burger
                "https://images.unsplash.com/photo-1551782450-a2132b4ba21d?w=800&h=600&fit=crop&crop=center",  # Pasta
                "https://images.unsplash.com/photo-1563379091339-03246963d7d3?w=800&h=600&fit=crop&crop=center",  # Soup
            ]
            
            # Return a random image from the list based on recipe title hash
            import hashlib
            hash_value = int(hashlib.md5(recipe_title.encode()).hexdigest(), 16)
            selected_image = hardcoded_image_urls[hash_value % len(hardcoded_image_urls)]
            
            logger.info("Using hardcoded recipe image for testing", recipe_title=recipe_title, image_url=selected_image)
            return selected_image
            
        except Exception as e:
            logger.error("Failed to generate recipe image", error=str(e))
            # Return a default fallback image
            return "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=800&h=600&fit=crop&crop=center"
    
    def _call_openai_image(self, prompt: str):
        """Make synchronous call to OpenAI Images API"""
        try:
            response = self.client.images.generate(
                model=settings.OPENAI_IMAGE_MODEL,
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            return response
        except Exception as e:
            logger.error("OpenAI Image API call failed", error=str(e))
            return None
    
    def _build_image_prompt(
        self,
        recipe_title: str,
        cuisine: Optional[str] = None,
        ingredients: Optional[List[str]] = None
    ) -> str:
        """Build prompt for recipe image generation"""
        
        prompt = f"Professional food photography of {recipe_title}, beautifully plated and garnished"
        
        if cuisine:
            prompt += f", {cuisine} cuisine style"
        
        if ingredients:
            main_ingredients = ingredients[:3]  # Use first 3 ingredients
            prompt += f", featuring {', '.join(main_ingredients)}"
        
        prompt += ", high-quality restaurant presentation, natural lighting, appetizing, detailed, realistic, 4k quality"
        
        return prompt
    
    async def get_ingredient_suggestions(self, partial_ingredient: str) -> List[str]:
        """Get ingredient suggestions for autocomplete"""
        if not self.client:
            return []
        
        try:
            prompt = f"""Suggest 10 common cooking ingredients that start with or contain "{partial_ingredient}". 
            Respond with a JSON array of strings, no explanations.
            Example: ["ingredient1", "ingredient2", ...]"""
            
            try:
                response = await asyncio.to_thread(
                    self.client.chat.completions.create,
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
            except Exception:
                # Fallback without JSON mode
                response = await asyncio.to_thread(
                    self.client.chat.completions.create,
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt + " Return as JSON array."}],
                    max_tokens=200,
                    temperature=0.1
                )
            
            result = json.loads(response.choices[0].message.content)
            if isinstance(result, dict) and 'suggestions' in result:
                return result['suggestions'][:10]
            elif isinstance(result, list):
                return result[:10]
            
        except Exception as e:
            logger.error("Failed to get ingredient suggestions", error=str(e))
        
        return []
    
    async def get_recipe_variations(self, original_recipe: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recipe variations"""
        if not self.client:
            return []
        
        try:
            prompt = f"""Based on this recipe: {original_recipe.get('title', 'Unknown')}, 
            create 3 variations with different cooking methods, ingredients, or flavors.
            
            Original ingredients: {', '.join([ing.get('name', '') for ing in original_recipe.get('ingredients', [])])}
            
            Return as JSON object with "suggestions" array. Each suggestion should have:
            - title: variation name
            - description: brief description of the variation
            - key_changes: what makes this variation different
            
            Example format:
            {{
                "suggestions": [
                    {{
                        "title": "Variation Name",
                        "description": "Brief description of this variation",
                        "key_changes": "What makes this different from the original"
                    }}
                ]
            }}
            """
            
            try:
                response = await asyncio.to_thread(
                    self.client.chat.completions.create,
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=800,
                    temperature=0.8,
                    response_format={"type": "json_object"}
                )
            except Exception:
                # Fallback without JSON mode
                response = await asyncio.to_thread(
                    self.client.chat.completions.create,
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt + " Return as JSON object with suggestions array."}],
                    max_tokens=800,
                    temperature=0.8
                )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('suggestions', [])[:3]
            
        except Exception as e:
            logger.error("Failed to generate recipe variations", error=str(e))
            return []


# Global AI service instance
ai_service = AIService() 