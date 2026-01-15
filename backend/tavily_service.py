from tavily import TavilyClient
from typing import Dict, Any, Optional
from backend.config import TAVILY_CONFIG
from backend.logger import get_logger

logger = get_logger(__name__)


def search_recipes(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    Search for recipes using Tavily API.
    Returns the full Tavily response.
    """
    logger.info(
        "Searching Tavily API",
        extra={"query": query, "max_results": max_results}
    )
    
    api_key = TAVILY_CONFIG.get("api_key")
    
    if not api_key:
        logger.error("TAVILY_API_KEY not found in environment variables")
        raise ValueError("TAVILY_API_KEY not found in environment variables")
    
    try:
        tavily_client = TavilyClient(api_key=api_key)
        
        logger.debug("Calling Tavily API", extra={"query": query})
        response = tavily_client.search(
            query=query,
            include_answer=True,
            max_results=max_results
        )
        
        result_count = len(response.get("results", []))
        logger.info(
            "Tavily API search completed",
            extra={
                "query": query,
                "result_count": result_count,
                "response_time": response.get("response_time")
            }
        )
        
        return response
    except Exception as e:
        logger.error(
            "Tavily API search failed",
            exc_info=True,
            extra={"query": query, "error": str(e)}
        )
        raise


def select_best_result(tavily_response: Dict[str, Any]) -> tuple[int, Optional[Dict[str, Any]]]:
    """
    Select the result with the highest score from Tavily response.
    Returns (index, result_dict) or (0, None) if no results.
    """
    results = tavily_response.get("results", [])
    
    if not results:
        logger.debug("No results to select from")
        return (0, None)
    
    logger.debug(
        "Selecting best result",
        extra={"total_results": len(results)}
    )
    
    # Find result with highest score
    best_index = 0
    best_score = results[0].get("score", 0.0)
    
    for i, result in enumerate(results):
        score = result.get("score", 0.0)
        if score > best_score:
            best_score = score
            best_index = i
    
    selected_result = results[best_index]
    logger.info(
        "Best result selected",
        extra={
            "selected_index": best_index,
            "score": best_score,
            "url": selected_result.get("url")
        }
    )
    
    return (best_index, selected_result)
