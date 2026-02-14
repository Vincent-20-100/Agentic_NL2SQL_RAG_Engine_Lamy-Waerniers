"""
SQL tool - async wrapper for database queries
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
sync_sql_tool = _tools_module.execute_sql_query


async def execute_sql_async(query: str, db_name: str, catalog: dict) -> dict:
    """
    Execute SQL query asynchronously

    Uses asyncio.to_thread() to run sync tool in thread pool
    (True async with aiopg/asyncpg can be future optimization)

    Returns dict with results or error
    """
    try:
        # Run sync tool in thread pool
        result_json = await asyncio.to_thread(
            sync_sql_tool.invoke,
            {
                "query": query,
                "db_name": db_name,
                "state_catalog": catalog
            }
        )

        # Parse JSON result
        result = json.loads(result_json)

        return {
            "results": result if not isinstance(result, dict) or "error" not in result else [],
            "error": result.get("error") if isinstance(result, dict) else None,
            "row_count": len(result) if isinstance(result, list) else 0
        }
    except Exception as e:
        return {
            "results": [],
            "error": f"SQL execution failed: {str(e)}",
            "row_count": 0
        }
