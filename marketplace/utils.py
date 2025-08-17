import os
from PIL import Image
from io import BytesIO
from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile
import uuid


def optimize_image(image_file, max_width=800, max_height=600, quality=85):
    """
    Optimize and resize an uploaded image to fit within specified dimensions.
    
    Args:
        image_file: The uploaded image file
        max_width: Maximum width in pixels (default: 800)
        max_height: Maximum height in pixels (default: 600)
        quality: JPEG quality (1-100, default: 85)
    
    Returns:
        InMemoryUploadedFile: Optimized image file
    """
    try:
        # Open the image
        img = Image.open(image_file)
        
        # Convert to RGB if necessary (for JPEG compatibility)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create a white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Calculate new dimensions while maintaining aspect ratio
        width, height = img.size
        
        # Check if resizing is needed
        if width <= max_width and height <= max_height:
            # Image is already within limits, just optimize quality
            pass
        else:
            # Calculate new dimensions
            ratio = min(max_width / width, max_height / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            
            # Resize the image
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Save the optimized image to memory
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        # Generate a unique filename
        file_extension = 'jpg'
        filename = f"{uuid.uuid4().hex}.{file_extension}"
        
        # Create a new InMemoryUploadedFile
        optimized_file = InMemoryUploadedFile(
            output,
            'ImageField',
            filename,
            'image/jpeg',
            output.getbuffer().nbytes,
            None
        )
        
        return optimized_file
        
    except Exception as e:
        # If optimization fails, return the original file
        print(f"Image optimization failed: {e}")
        return image_file


def create_thumbnail(image_file, size=(200, 150), quality=80):
    """
    Create a thumbnail version of an image.
    
    Args:
        image_file: The uploaded image file
        size: Tuple of (width, height) for thumbnail
        quality: JPEG quality (1-100, default: 80)
    
    Returns:
        InMemoryUploadedFile: Thumbnail image file
    """
    try:
        # Open the image
        img = Image.open(image_file)
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Create thumbnail
        img.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Save the thumbnail to memory
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        # Generate a unique filename
        filename = f"thumb_{uuid.uuid4().hex}.jpg"
        
        # Create a new InMemoryUploadedFile
        thumbnail_file = InMemoryUploadedFile(
            output,
            'ImageField',
            filename,
            'image/jpeg',
            output.getbuffer().nbytes,
            None
        )
        
        return thumbnail_file
        
    except Exception as e:
        print(f"Thumbnail creation failed: {e}")
        return image_file


def validate_image_file(image_file, max_size_mb=5):
    """
    Validate an uploaded image file.
    
    Args:
        image_file: The uploaded image file
        max_size_mb: Maximum file size in MB (default: 5)
    
    Returns:
        tuple: (is_valid, error_message)
    """
    # Check file size
    max_size_bytes = max_size_mb * 1024 * 1024
    if image_file.size > max_size_bytes:
        return False, f"Image file size must be less than {max_size_mb}MB"
    
    # Check file type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
    if image_file.content_type not in allowed_types:
        return False, "Only JPEG, PNG, GIF, and WebP images are allowed"
    
    # Try to open the image to verify it's valid
    try:
        img = Image.open(image_file)
        img.verify()
        image_file.seek(0)  # Reset file pointer
    except Exception:
        return False, "Invalid image file"
    
    return True, None
