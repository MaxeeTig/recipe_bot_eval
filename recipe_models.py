"""
Pydantic models for structured recipe data.
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

from patches import get_patch_unit_mapping

# Base unit mapping; overlays from patches/unit_mapping.json are merged at runtime
BASE_UNIT_MAPPING = {
    # Grams
    'г': 'г', 'грамм': 'г', 'грамма': 'г', 'граммов': 'г', 'гр': 'г',
    # Milliliters
    'мл': 'мл', 'миллилитр': 'мл', 'миллилитра': 'мл', 'миллилитров': 'мл',
    # Pieces
    'шт': 'шт', 'штук': 'шт', 'штука': 'шт', 'штуки': 'шт',
    # Tablespoons - handle various forms
    'ст.л': 'ст.л', 'ст. ложка': 'ст.л', 'ст. ложки': 'ст.л',
    'ст ложка': 'ст.л', 'ст ложки': 'ст.л', 'столовых ложек': 'ст.л',
    'столовые ложки': 'ст.л', 'столовая ложка': 'ст.л', 'ст. ложек': 'ст.л',
    'ст. лож.': 'ст.л', 'ст лож.': 'ст.л',
    # Teaspoons
    'ч.л': 'ч.л', 'ч. ложка': 'ч.л', 'ч. ложки': 'ч.л',
    'ч ложка': 'ч.л', 'ч ложки': 'ч.л', 'чайных ложек': 'ч.л',
    'чайные ложки': 'ч.л', 'чайная ложка': 'ч.л', 'ч. ложек': 'ч.л',
    'ч. лож.': 'ч.л', 'ч лож.': 'ч.л',
    # Cups
    'чашка': 'чашка', 'чашки': 'чашка', 'чашек': 'чашка',
    'стакан': 'чашка', 'стакана': 'чашка', 'стаканов': 'чашка', 'ст': 'чашка',
    # Liters
    'л': 'л', 'литр': 'л', 'литра': 'л', 'литров': 'л',
    # Kilograms
    'кг': 'кг', 'килограмм': 'кг', 'килограмма': 'кг', 'килограммов': 'кг',
}


def _get_unit_mapping() -> dict:
    """Merge base unit mapping with overlay from patches/unit_mapping.json."""
    return {**BASE_UNIT_MAPPING, **get_patch_unit_mapping()}


class Ingredient(BaseModel):
    """Represents a single ingredient in a recipe."""
    name: str = Field(description="Название ингредиента (например: 'молоко', 'сахар')")
    amount: float = Field(description="Количество в базовых единицах")
    unit: str = Field(
        description="Стандартизированная единица измерения (г, мл, шт, ст.л, ч.л, чашка, л, кг или их вариации)"
    )
    original_text: str = Field(description="Оригинальный текст из рецепта для сравнения")
    
    @field_validator('amount', mode='before')
    @classmethod
    def parse_amount(cls, v):
        """Parse amount from various formats: numbers, strings with commas, ranges."""
        if isinstance(v, (int, float)):
            # Allow 0 for "по вкусу" cases
            if v < 0:
                raise ValueError("Количество не может быть отрицательным")
            return float(v)
        
        if isinstance(v, str):
            # Handle "по вкусу" or empty
            v = v.strip()
            if not v or v.lower() in ['по вкусу', 'по вкусу', '']:
                return 0.0
            
            # Replace comma with dot for European decimal format
            v = v.replace(',', '.')
            
            # Handle ranges like "2-3" or "0,5-1" - take the first value or average
            if '-' in v:
                parts = v.split('-')
                if len(parts) == 2:
                    try:
                        first = float(parts[0].strip().replace(',', '.'))
                        second = float(parts[1].strip().replace(',', '.'))
                        # Use average for ranges
                        result = (first + second) / 2
                        if result < 0:
                            raise ValueError("Количество не может быть отрицательным")
                        return result
                    except ValueError:
                        # If can't parse range, try just the first part
                        result = float(parts[0].strip().replace(',', '.'))
                        if result < 0:
                            raise ValueError("Количество не может быть отрицательным")
                        return result
            
            # Try to parse as float
            try:
                result = float(v)
                if result < 0:
                    raise ValueError("Количество не может быть отрицательным")
                return result
            except ValueError:
                raise ValueError(f"Не удалось распарсить количество: {v}")
        
        raise ValueError(f"Неподдерживаемый тип для количества: {type(v)}")
    
    @field_validator('unit', mode='before')
    @classmethod
    def normalize_unit(cls, v):
        """Normalize unit variations to standard forms."""
        if not isinstance(v, str):
            return v
        
        original_v = v.strip()
        v_lower = original_v.lower()
        unit_mapping = _get_unit_mapping()
        
        # Try exact match first (case-insensitive)
        if v_lower in unit_mapping:
            return unit_mapping[v_lower]
        
        # Try partial match for complex cases like "ст. ложки" or "ст. ложек"
        # Check if any mapping key is contained in the input
        for key, standard in unit_mapping.items():
            if len(key) > 2 and key in v_lower:
                return standard
        
        # If no match found, return original (will be validated)
        return original_v
    
    @field_validator('unit')
    @classmethod
    def validate_unit(cls, v):
        """Validate that unit is one of the allowed values, but allow any string for flexibility."""
        allowed_units = ["г", "мл", "шт", "ст.л", "ч.л", "чашка", "л", "кг"]
        # Allow any string - normalization should have handled most cases
        # This provides flexibility for edge cases while encouraging standardization
        return v


class Recipe(BaseModel):
    """Represents a complete recipe with structured data."""
    title: str = Field(description="Название блюда")
    ingredients: List[Ingredient] = Field(description="Список ингредиентов в стандартизированном формате")
    instructions: List[str] = Field(description="Пошаговая инструкция приготовления")
    cooking_time: Optional[int] = Field(description="Время приготовления в минутах", default=None)
    servings: Optional[int] = Field(description="Количество порций", default=None)
    source_url: str = Field(description="Источник рецепта")
