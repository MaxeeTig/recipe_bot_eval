from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal
import json


class Ingredient(BaseModel):
    name: str = Field(description="Название ингредиента (например: 'молоко', 'сахар')")
    amount: float = Field(description="Количество в базовых единицах")
    unit: Literal["г", "мл", "шт", "ст.л", "ч.л", "чашка", "л", "кг"] = Field(
        description="Стандартизированная единица измерения"
    )
    original_text: str = Field(
        description="Оригинальный текст из рецепта для сравнения"
    )

    @validator("amount")
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Количество должно быть положительным")
        return v


class Recipe(BaseModel):
    intro: str = Field(
        description="Короткое введение о блюде (например: 'борщ - традиционное блюдо русской кухни'"
    )
    title: str = Field(description="Название блюда")
    ingredients: List[Ingredient] = Field(
        description="Список ингредиентов в стандартизированном формате"
    )
    instructions: List[str] = Field(
        description="Пошаговая инструкция приготовления"
    )
    cooking_time: Optional[int] = Field(
        description="Время приготовления в минутах"
    )
    servings: Optional[int] = Field(description="Количество порций")
    source_url: str = Field(description="Источник рецепта")
    regards: str = Field(
        description="Доброе пожелание пользователю (например: 'пусть ваш борщ будет наваристым и сытным')"
    )

    def to_dict(self) -> dict:
        """Convert Recipe to dictionary for JSON serialization."""
        return self.dict()

    @classmethod
    def from_dict(cls, data: dict) -> "Recipe":
        """Create Recipe from dictionary."""
        return cls(**data)

    def to_json(self) -> str:
        """Convert Recipe to JSON string."""
        return self.json(ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "Recipe":
        """Create Recipe from JSON string."""
        data = json.loads(json_str)
        return cls(**data)
