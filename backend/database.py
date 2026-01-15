import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from backend.config import DATABASE_PATH
from backend.logger import get_logger

logger = get_logger(__name__)


def get_db_connection():
    """Get database connection, creating database file if it doesn't exist."""
    # Ensure data directory exists
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    logger.debug("Opening database connection", extra={"database_path": str(DATABASE_PATH)})
    try:
        conn = sqlite3.connect(str(DATABASE_PATH))
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(
            "Failed to connect to database",
            exc_info=True,
            extra={"database_path": str(DATABASE_PATH), "error": str(e)}
        )
        raise


def init_database():
    """Initialize database schema."""
    logger.info("Initializing database schema")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        logger.debug("Creating recipes table if not exists")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                id TEXT PRIMARY KEY,
                query TEXT NOT NULL,
                tavily_response TEXT NOT NULL,
                selected_result_index INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'stored',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("Database schema initialized successfully")
    except Exception as e:
        logger.error(
            "Failed to initialize database schema",
            exc_info=True,
            extra={"error": str(e)}
        )
        raise


def create_recipe(
    recipe_id: str,
    query: str,
    tavily_response: Dict[str, Any],
    selected_result_index: int,
    status: str = "stored"
) -> Dict[str, Any]:
    """Create a new recipe entry in the database."""
    logger.debug(
        "Creating recipe",
        extra={"recipe_id": recipe_id, "query": query, "status": status}
    )
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        now = datetime.utcnow().isoformat()
        
        cursor.execute("""
            INSERT INTO recipes (id, query, tavily_response, selected_result_index, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            recipe_id,
            query,
            json.dumps(tavily_response, ensure_ascii=False),
            selected_result_index,
            status,
            now,
            now
        ))
        
        conn.commit()
        conn.close()
        
        logger.info("Recipe created successfully", extra={"recipe_id": recipe_id})
        return get_recipe(recipe_id)
    except Exception as e:
        logger.error(
            "Failed to create recipe",
            exc_info=True,
            extra={"recipe_id": recipe_id, "error": str(e)}
        )
        raise


def get_recipe(recipe_id: str) -> Optional[Dict[str, Any]]:
    """Get a recipe by ID."""
    logger.debug("Getting recipe from database", extra={"recipe_id": recipe_id})
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            logger.debug("Recipe found", extra={"recipe_id": recipe_id})
            return dict(row)
        
        logger.debug("Recipe not found", extra={"recipe_id": recipe_id})
        return None
    except Exception as e:
        logger.error(
            "Failed to get recipe",
            exc_info=True,
            extra={"recipe_id": recipe_id, "error": str(e)}
        )
        raise


def get_all_recipes(exclude_deleted: bool = True) -> List[Dict[str, Any]]:
    """Get all recipes, optionally excluding deleted ones."""
    logger.debug(
        "Getting all recipes",
        extra={"exclude_deleted": exclude_deleted}
    )
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if exclude_deleted:
            cursor.execute("SELECT * FROM recipes WHERE status != 'deleted' ORDER BY created_at DESC")
        else:
            cursor.execute("SELECT * FROM recipes ORDER BY created_at DESC")
        
        rows = cursor.fetchall()
        conn.close()
        
        result = [dict(row) for row in rows]
        logger.debug(
            "Recipes retrieved",
            extra={"count": len(result), "exclude_deleted": exclude_deleted}
        )
        return result
    except Exception as e:
        logger.error(
            "Failed to get all recipes",
            exc_info=True,
            extra={"exclude_deleted": exclude_deleted, "error": str(e)}
        )
        raise


def update_recipe_status(recipe_id: str, status: str) -> Optional[Dict[str, Any]]:
    """Update recipe status (e.g., mark as deleted)."""
    logger.debug(
        "Updating recipe status",
        extra={"recipe_id": recipe_id, "new_status": status}
    )
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        now = datetime.utcnow().isoformat()
        
        cursor.execute("""
            UPDATE recipes 
            SET status = ?, updated_at = ?
            WHERE id = ?
        """, (status, now, recipe_id))
        
        conn.commit()
        conn.close()
        
        logger.info(
            "Recipe status updated",
            extra={"recipe_id": recipe_id, "new_status": status}
        )
        return get_recipe(recipe_id)
    except Exception as e:
        logger.error(
            "Failed to update recipe status",
            exc_info=True,
            extra={"recipe_id": recipe_id, "status": status, "error": str(e)}
        )
        raise


def delete_recipe(recipe_id: str) -> bool:
    """Soft delete a recipe (mark as deleted)."""
    logger.debug("Soft deleting recipe", extra={"recipe_id": recipe_id})
    result = update_recipe_status(recipe_id, "deleted")
    success = result is not None
    
    if success:
        logger.info("Recipe soft deleted successfully", extra={"recipe_id": recipe_id})
    else:
        logger.warning("Recipe not found for deletion", extra={"recipe_id": recipe_id})
    
    return success
