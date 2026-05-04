import sys
import os

# Manually add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp_tools.vision_tool import get_image_embedding