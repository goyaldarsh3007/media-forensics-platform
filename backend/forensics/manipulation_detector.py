import os
from PIL import Image, ImageChops
import numpy as np

def detect_manipulation(image_path, quality=95, scale=30):
    """
    Applies Error Level Analysis (ELA) to identify potential tampering.
    Saves the ELA difference map next to the original image and calculates
    localized block-level compression variances.
    """
    # Get directory and file base
    dir_name = os.path.dirname(image_path)
    base_name = os.path.basename(image_path)
    name, ext = os.path.splitext(base_name)
    
    ela_filename = f"{name}_ela.jpg"
    ela_path = os.path.join(dir_name, ela_filename)
    
    # Temp resaved image path
    temp_path = os.path.join(dir_name, f"{name}_temp_resave.jpg")
    
    try:
        original = Image.open(image_path).convert("RGB")
        
        # Save with target quality
        original.save(temp_path, "JPEG", quality=quality)
        
        # Re-open
        resaved = Image.open(temp_path)
        
        # Absolute difference
        diff = ImageChops.difference(original, resaved)
        
        # Calculate block stats using numpy
        arr = np.array(diff.convert("L"))
        h, w = arr.shape
        
        # Calculate global statistics
        global_avg = float(np.mean(arr))
        
        # Calculate block-level variance (32x32 pixel blocks)
        block_size = 32
        block_averages = []
        for y in range(0, h - block_size + 1, block_size):
            for x in range(0, w - block_size + 1, block_size):
                block = arr[y:y+block_size, x:x+block_size]
                block_averages.append(float(np.mean(block)))
                
        max_block = max(block_averages) if block_averages else 0.0
        ratio = max_block / (global_avg + 0.01)
        
        # Scale difference map to make it visible
        scaled_diff = Image.eval(diff, lambda x: x * scale)
        scaled_diff.save(ela_path, "JPEG")
        
        # Interpret stats
        # Higher thresholds prevent false positives on high-contrast text or natural textures.
        if ratio >= 8.0 and max_block >= 3.0:
            verdict = "Localized compression discrepancies detected. Spliced or modified elements typically stand out as bright clusters in the ELA heatmap."
            status = "warning"
        elif ratio >= 5.0 and max_block >= 1.5:
            verdict = "Moderate localized variance (Check ELA heatmap below for selective editing)."
            status = "neutral"
        elif global_avg >= 4.0:
            verdict = "High overall compression variance detected. The image may have been resaved multiple times at different quality levels."
            status = "neutral"
        else:
            verdict = "Low overall compression variance. Scan the ELA heatmap below for any bright localized highlights."
            status = "success"
            
        return {
            "ela_score": round(global_avg, 4),
            "max_block_ela": round(max_block, 4),
            "max_to_avg_ratio": round(ratio, 4),
            "ela_filename": ela_filename,
            "verdict": verdict,
            "status": status
        }
    except Exception as e:
        print("Error performing ELA:", e)
        return {
            "ela_score": 0.0,
            "max_block_ela": 0.0,
            "max_to_avg_ratio": 0.0,
            "ela_filename": None,
            "verdict": f"Error performing ELA: {str(e)}",
            "status": "neutral"
        }
    finally:
        # Cleanup temp file
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
