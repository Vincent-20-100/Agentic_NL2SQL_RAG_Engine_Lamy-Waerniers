"""
Semantic search tool - async wrapper for vector search
"""
import asyncio
import json
import os
import importlib.util

# Import from code/tools.py module file (not code/tools/ package)
# Due to naming conflict, we use importlib to load the specific file
_tools_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tools.py")
_spec = importlib.util.spec_from_file_location("_code_tools_module", _tools_file_path)
_tools_module = importlib.util.module_from_spec(_spec)

# We need to setup the module's environment before loading
# so it can find its imports (config, etc.)
import sys
_parent_dir = os.path.dirname(os.path.dirname(__file__))
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

_spec.loader.exec_module(_tools_module)
sync_semantic_tool = _tools_module.semantic_search


async def execute_semantic_async(query: str, n_results: int = 5) -> dict:
    """
    Execute semantic search asynchronously

    Returns dict with results or error
    """
    try:
        # Run sync tool in thread pool
        result_json = await asyncio.to_thread(
            sync_semantic_tool.invoke,
            {
                "query": query,
                "n_results": n_results
            }
        )

        # Parse JSON result
        result = json.loads(result_json)

        if isinstance(result, dict) and "error" in result:
            return {
                "results": [],
                "error": result["error"]
            }

        return {
            "results": result if isinstance(result, list) else [],
            "error": None
        }
    except Exception as e:
        return {
            "results": [],
            "error": f"Semantic search failed: {str(e)}"
        }
