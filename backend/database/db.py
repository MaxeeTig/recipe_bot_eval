"""
SQLite database operations for recipe processing pipeline.
Refactored from database.py with logging support.
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
import sys
from pathlib import Path

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config_section import DATA_DIR, DB_PATH
from backend.logging_config import get_logger

logger = get_logger(__name__)


def init_database() -> None:
    """
    Initialize SQLite database and create recipes table if it doesn't exist.
    Creates data directory if needed.
    """
    logger.debug("Initializing database")
    # Ensure data directory exists
    DATA_DIR.mkdir(exist_ok=True)
    
    # Connect to database (creates file if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create recipes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_name TEXT NOT NULL,
            source_url TEXT NOT NULL,
            raw_title TEXT NOT NULL,
            raw_recipe_text TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'new',
            parsed_recipe TEXT,
            error_type TEXT,
            error_message TEXT,
            error_traceback TEXT,
            llm_response_text TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            parsed_at TEXT
        )
    """)
    
    # Add llm_response_text column if it doesn't exist (migration for existing databases)
    # Check if column exists by querying table info
    cursor.execute("PRAGMA table_info(recipes)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'llm_response_text' not in columns:
        try:
            cursor.execute("ALTER TABLE recipes ADD COLUMN llm_response_text TEXT")
            logger.info("Added llm_response_text column to recipes table")
        except sqlite3.OperationalError:
            # Column already exists or other error, ignore
            pass
    
    # Create error_analyses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS error_analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            analysis_report TEXT NOT NULL,
            recommendations_summary TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()
    logger.debug("Database initialized successfully")


def save_raw_recipe(recipe_name: str, source_url: str, raw_title: str, raw_recipe_text: List[str]) -> int:
    """
    Save raw recipe data to database with status 'new'.
    
    Args:
        recipe_name: Search query used to find the recipe
        source_url: URL of the recipe page
        raw_title: Title of the recipe
        raw_recipe_text: List of recipe text strings
        
    Returns:
        ID of the inserted recipe
    """
    logger.info(f"Saving raw recipe: {raw_title}")
    init_database()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Convert recipe_text list to JSON string
    recipe_text_json = json.dumps(raw_recipe_text, ensure_ascii=False)
    
    # Get current timestamp
    now = datetime.now().isoformat()
    
    cursor.execute("""
        INSERT INTO recipes (
            recipe_name, source_url, raw_title, raw_recipe_text,
            status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (recipe_name, source_url, raw_title, recipe_text_json, 'new', now, now))
    
    recipe_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    logger.info(f"Saved raw recipe with ID: {recipe_id}")
    return recipe_id


def get_recipes_by_status(status: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get all recipes with the specified status, or all recipes if status is None.
    
    Args:
        status: Recipe status ('new', 'success', 'failure') or None for all
        
    Returns:
        List of recipe dictionaries
    """
    logger.debug(f"Getting recipes by status: {status or 'all'}")
    init_database()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    cursor = conn.cursor()
    
    if status:
        cursor.execute("""
            SELECT * FROM recipes WHERE status = ? ORDER BY created_at DESC
        """, (status,))
    else:
        cursor.execute("""
            SELECT * FROM recipes ORDER BY created_at DESC
        """)
    
    rows = cursor.fetchall()
    conn.close()
    
    # Convert rows to dictionaries
    recipes = []
    for row in rows:
        recipe = dict(row)
        # Parse JSON fields
        if recipe['raw_recipe_text']:
            try:
                recipe['raw_recipe_text'] = json.loads(recipe['raw_recipe_text'])
            except json.JSONDecodeError:
                pass
        if recipe['parsed_recipe']:
            try:
                recipe['parsed_recipe'] = json.loads(recipe['parsed_recipe'])
            except json.JSONDecodeError:
                pass
        recipes.append(recipe)
    
    logger.debug(f"Retrieved {len(recipes)} recipes")
    return recipes


def get_recipe_by_id(recipe_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a single recipe by ID.
    
    Args:
        recipe_id: Recipe ID
        
    Returns:
        Recipe dictionary or None if not found
    """
    logger.debug(f"Getting recipe by ID: {recipe_id}")
    init_database()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        logger.warning(f"Recipe with ID {recipe_id} not found")
        return None
    
    recipe = dict(row)
    # Parse JSON fields
    if recipe['raw_recipe_text']:
        try:
            recipe['raw_recipe_text'] = json.loads(recipe['raw_recipe_text'])
        except json.JSONDecodeError:
            pass
    if recipe['parsed_recipe']:
        try:
            recipe['parsed_recipe'] = json.loads(recipe['parsed_recipe'])
        except json.JSONDecodeError:
            pass
    
    logger.debug(f"Retrieved recipe ID {recipe_id}")
    return recipe


def update_recipe_success(recipe_id: int, parsed_recipe: Any) -> None:
    """
    Update recipe with parsed data and set status to 'success'.
    
    Args:
        recipe_id: Recipe ID
        parsed_recipe: Recipe Pydantic model or dict to store as JSON
    """
    logger.info(f"Updating recipe {recipe_id} with success status")
    init_database()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Convert parsed recipe to JSON string
    if hasattr(parsed_recipe, 'model_dump'):
        # Pydantic model
        parsed_json = json.dumps(parsed_recipe.model_dump(), ensure_ascii=False)
    elif isinstance(parsed_recipe, dict):
        parsed_json = json.dumps(parsed_recipe, ensure_ascii=False)
    else:
        raise ValueError("parsed_recipe must be a Pydantic model or dict")
    
    now = datetime.now().isoformat()
    
    cursor.execute("""
        UPDATE recipes
        SET status = ?, parsed_recipe = ?, parsed_at = ?, updated_at = ?
        WHERE id = ?
    """, ('success', parsed_json, now, now, recipe_id))
    
    conn.commit()
    conn.close()
    logger.info(f"Recipe {recipe_id} updated to success status")


def update_recipe_failure(recipe_id: int, error_type: str, error_message: str, error_traceback: str, llm_response_text: Optional[str] = None) -> None:
    """
    Update recipe with error information and set status to 'failure'.
    
    Args:
        recipe_id: Recipe ID
        error_type: Exception class name
        error_message: Error message
        error_traceback: Full traceback string
        llm_response_text: Raw LLM response text before cleaning (optional)
    """
    logger.warning(f"Updating recipe {recipe_id} with failure status: {error_type}")
    init_database()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    cursor.execute("""
        UPDATE recipes
        SET status = ?, error_type = ?, error_message = ?, error_traceback = ?, llm_response_text = ?, updated_at = ?
        WHERE id = ?
    """, ('failure', error_type, error_message, error_traceback, llm_response_text, now, recipe_id))
    
    conn.commit()
    conn.close()
    logger.warning(f"Recipe {recipe_id} updated to failure status")


def save_error_analysis(recipe_id: int, analysis_report: dict, recommendations_summary: Optional[str] = None) -> int:
    """
    Save error analysis report to database.
    
    Args:
        recipe_id: Recipe ID that was analyzed
        analysis_report: Analysis report dictionary (will be stored as JSON)
        recommendations_summary: Optional summary text of recommendations
        
    Returns:
        ID of the inserted analysis
    """
    logger.info(f"Saving error analysis for recipe {recipe_id}")
    init_database()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Convert analysis report to JSON string
    analysis_json = json.dumps(analysis_report, ensure_ascii=False)
    
    now = datetime.now().isoformat()
    
    cursor.execute("""
        INSERT INTO error_analyses (
            recipe_id, analysis_report, recommendations_summary, created_at
        ) VALUES (?, ?, ?, ?)
    """, (recipe_id, analysis_json, recommendations_summary, now))
    
    analysis_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    logger.info(f"Saved error analysis with ID: {analysis_id}")
    return analysis_id


def get_error_analyses_by_recipe_id(recipe_id: int) -> List[Dict[str, Any]]:
    """
    Get all error analyses for a specific recipe.
    
    Args:
        recipe_id: Recipe ID
        
    Returns:
        List of analysis dictionaries
    """
    logger.debug(f"Getting error analyses for recipe {recipe_id}")
    init_database()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM error_analyses WHERE recipe_id = ? ORDER BY created_at DESC
    """, (recipe_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    # Convert rows to dictionaries
    analyses = []
    for row in rows:
        analysis = dict(row)
        # Parse JSON fields
        if analysis['analysis_report']:
            try:
                analysis['analysis_report'] = json.loads(analysis['analysis_report'])
            except json.JSONDecodeError:
                pass
        analyses.append(analysis)
    
    logger.debug(f"Retrieved {len(analyses)} analyses for recipe {recipe_id}")
    return analyses


def get_recipe_stats(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get recipe statistics: total, counts by status, and by error_type for failures.
    
    Args:
        date_from: Optional ISO date or datetime; filter recipes with created_at >= date_from
        date_to: Optional ISO date or datetime (inclusive); if date-only (no 'T'), end of day is used
        
    Returns:
        Dict with total, by_status (new, success, failure), by_error_type (for status=failure)
    """
    logger.debug(f"Getting recipe stats (date_from={date_from}, date_to={date_to})")
    init_database()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    where_clauses = []
    params = []
    if date_from is not None:
        where_clauses.append("created_at >= ?")
        params.append(date_from)
    if date_to is not None:
        date_to_val = date_to if "T" in date_to else f"{date_to}T23:59:59.999999"
        where_clauses.append("created_at <= ?")
        params.append(date_to_val)
    
    where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
    
    cursor.execute(f"SELECT status, error_type FROM recipes{where_sql}", params)
    rows = cursor.fetchall()
    conn.close()
    
    total = len(rows)
    by_status = {"new": 0, "success": 0, "failure": 0}
    by_error_type = {}
    
    for row in rows:
        st = row["status"]
        et = row["error_type"]
        if st in by_status:
            by_status[st] += 1
        if st == "failure" and et:
            by_error_type[et] = by_error_type.get(et, 0) + 1
    
    return {
        "total": total,
        "by_status": by_status,
        "by_error_type": by_error_type if by_error_type else None
    }


def delete_recipe(recipe_id: int) -> bool:
    """
    Delete a recipe and its associated error analyses.
    
    Args:
        recipe_id: Recipe ID to delete
        
    Returns:
        True if recipe was deleted, False if not found
    """
    logger.info(f"Deleting recipe {recipe_id}")
    init_database()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if recipe exists
    cursor.execute("SELECT id FROM recipes WHERE id = ?", (recipe_id,))
    if not cursor.fetchone():
        conn.close()
        logger.warning(f"Recipe {recipe_id} not found for deletion")
        return False
    
    # Delete recipe (cascade will delete analyses due to FOREIGN KEY constraint)
    cursor.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
    
    conn.commit()
    conn.close()
    
    logger.info(f"Deleted recipe {recipe_id}")
    return True
