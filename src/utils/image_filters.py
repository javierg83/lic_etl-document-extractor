import io
from PIL import Image, ImageEnhance

def enhance_image_contrast(image_bytes: bytes, factor: float = 2.0) -> bytes:
    """
    Mejora el contraste de una imagen (bytes) para facilitar el OCR.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        enhancer = ImageEnhance.Contrast(image)
        enhanced_image = enhancer.enhance(factor)
        
        # Convertir a escala de grises (binarización simple)
        enhanced_image = enhanced_image.convert('L')
        
        output_buffer = io.BytesIO()
        enhanced_image.save(output_buffer, format='PNG')
        return output_buffer.getvalue()
    except Exception as e:
        print(f"Error mejorando contraste de imagen: {e}")
        return image_bytes
