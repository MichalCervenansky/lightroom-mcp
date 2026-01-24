from mcp.server.fastmcp import FastMCP
from lrc_client import LrCClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP Server
mcp = FastMCP("Lightroom MCP")

# Initialize LrC Client
lrc = LrCClient()

@mcp.tool()
def get_studio_info() -> str:
    """
    Get information about the active Lightroom Catalog.
    Returns JSON string with catalog name, path, and plugin version.
    """
    try:
        result = lrc.send_command("get_studio_info")
        if result and "result" in result:
            return str(result["result"])
        elif result and "error" in result:
            return f"Error: {result['error']['message']}"
        else:
            return "Error: No response from Lightroom"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def get_selection() -> str:
    """
    Get the list of currently selected photos in Lightroom.
    Returns JSON string with photo details (filename, rating, label, etc.).
    """
    try:
        result = lrc.send_command("get_selection")
        if result and "result" in result:
            return str(result["result"])
        elif result and "error" in result:
            return f"Error: {result['error']['message']}"
        else:
            return "Error: No response from Lightroom"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def set_rating(rating: int) -> str:
    """
    Set the star rating for the currently selected photos.
    
    Args:
        rating: Integer between 0 and 5.
    """
    if not (0 <= rating <= 5):
        return "Error: Rating must be between 0 and 5"

    try:
        result = lrc.send_command("set_metadata", {"rating": rating})
        if result and "result" in result:
            return "Success"
        elif result and "error" in result:
            return f"Error: {result['error']['message']}"
        else:
            return "Error: No response from Lightroom"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def set_label(label: str) -> str:
    """
    Set the color label for the currently selected photos.
    
    Args:
        label: One of 'Red', 'Yellow', 'Green', 'Blue', 'Purple', 'None'.
    """
    valid_labels = ['Red', 'Yellow', 'Green', 'Blue', 'Purple', 'None']
    if label not in valid_labels:
        return f"Error: Label must be one of {valid_labels}"

    try:
        # LrC often expects lower case or specific string, but 'Red' usually works or 'red'.
        # We will pass it as is, or lowercase it if command handler expects it.
        # LrC SDK: 'red', 'yellow', etc.
        result = lrc.send_command("set_metadata", {"label": label.lower()})
        if result and "result" in result:
            return "Success"
        elif result and "error" in result:
            return f"Error: {result['error']['message']}"
        else:
            return "Error: No response from Lightroom"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def set_caption(caption: str) -> str:
    """
    Set the caption for the currently selected photos.
    """
    try:
        result = lrc.send_command("set_metadata", {"caption": caption})
        if result and "result" in result:
            return "Success"
        elif result and "error" in result:
            return f"Error: {result['error']['message']}"
        else:
            return "Error: No response from Lightroom"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()
