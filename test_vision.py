import torch
from mcp_tools.vision_tool import get_image_embedding  # Assuming you saved it there
import os

def run_smoke_test():
    # 1. Define the path to your E-R Diagram
    # Based on your professional folder structure
    img_path = os.path.join('data', 'rag', 'images', 'er_diagram.png')
    
    print(f"--- Vision Smoke Test ---")
    print(f"Targeting: {img_path}")
    
    # 2. Attempt to generate the embedding
    vector = get_image_embedding(img_path)
    
    if vector is not None:
        print("✅ SUCCESS: Image loaded and embedded.")
        
        # 3. Verify the Dimensions
        # EfficientNet-B0 always outputs a 1280-length vector
        print(f"Vector Shape: {vector.shape}")
        
        # 4. Peek at the 'Math'
        # Showing the first 5 coordinates to prove it's not all zeros
        print(f"First 5 values: {vector[:5].tolist()}")
    else:
        print("❌ FAILED: Could not find or process the image. Check your path!")

if __name__ == "__main__":
    run_smoke_test()