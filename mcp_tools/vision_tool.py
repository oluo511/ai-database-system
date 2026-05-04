import os
import torch
import torchvision.transforms as transforms
from torchvision import models
from torchvision.models import EfficientNet_B0_Weights  
from PIL import Image

# Load EfficientNet-B0 (Remove the classifier head to get the vector)

# Transfer Learning. Loading in model that has learned to se lines and shapes
model = models.efficientnet_b0(weights=EfficientNet_B0_Weights.DEFAULT) 

# Replace Classifier with Identity
# allows the code to output the raw visual patterns it detects instead of a single label
# this gives a 1280 dimension vector instead of labels like "dog" or "cat"
model.classifier = torch.nn.Identity() 

# Evaluation mode ensures model behaves consistently (e.g., no dropout randomness) when generating embeddings
model.eval()

# Preprocessing pipeline (ImageNet standards)
transform = transforms.Compose([
    # Resize to 256 then crop to 224 to keep the center of the diagram so model can process correctly
    transforms.Resize(256),
    transforms.CenterCrop(224),
    # Convert pixels to math (Tensors) that the model can process
    transforms.ToTensor(),
    # Use ImageNet standards to center the color data for better accuracy
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406], 
        std=[0.229, 0.224, 0.225]
    )
])

def get_image_embedding(image_path):
    """Converts pixels to a 1280-dimensional vector."""
    if not os.path.exists(image_path):
        return None
    
    # Open and convert to RGB to handle .png transparency or black/white pics
    image = Image.open(image_path).convert('RGB')

    # Run the image through the preprocessing pipeline and add a 'batch' dimension
    input_tensor = transform(image).unsqueeze(0) 

    # Run inference without "learning" (gradients) to save memory and speed
    with torch.no_grad():
        embedding = model(input_tensor)

    # Remove the extra dimension to get a clean 1D vector of 1280 numbers    
    return embedding.squeeze()