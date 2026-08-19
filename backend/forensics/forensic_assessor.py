import os

def assess_forensics(analysis, ai_detection, manipulation_detection=None):
    """
    Evaluates multiple digital forensic signals to produce an overall assessment.
    
    Signals:
    1. AI Generation Classifier
    2. EXIF Metadata Integrity & Software tags
    3. File Header & Extension validation
    4. Image Manipulation (Error Level Analysis)
    """
    filename = analysis.get("filename", "")
    format_detected = analysis.get("format", "").upper()
    metadata = analysis.get("metadata", {})
    ai_prob = ai_detection.get("ai_probability", 0.0)
    
    # 1. AI Generation Signal
    ai_score = ai_prob
    if ai_prob >= 0.75:
        ai_status = "warning"
        ai_details = f"AI detector flags patterns typical of synthetic images with {ai_prob*100:.1f}% probability."
    elif ai_prob <= 0.25:
        ai_status = "success"
        ai_details = f"Image shows natural pixel distributions (Human probability: {(1-ai_prob)*100:.1f}%)."
    else:
        ai_status = "neutral"
        ai_details = f"AI classification is inconclusive (AI probability: {ai_prob*100:.1f}%)."
        
    # 2. Metadata Integrity Signal
    meta_score = 0.0
    meta_status = "neutral"
    meta_details = "No metadata was found."
    
    if metadata:
        # Check for editing software signatures
        software_keys = ["Image Software", "Software", "EXIF Software"]
        detected_software = None
        for key in software_keys:
            if key in metadata:
                detected_software = metadata[key]
                break
                
        editing_tools = ["photoshop", "gimp", "canva", "adobe", "figma", "stable diffusion", "midjourney", "dall-e", "pixlr"]
        has_editing_signature = False
        if detected_software:
            software_lower = detected_software.lower()
            if any(tool in software_lower for tool in editing_tools):
                has_editing_signature = True
                
        if has_editing_signature:
            meta_score = 1.0
            meta_status = "warning"
            meta_details = f"Image contains metadata signature from editing software: '{detected_software}'."
        else:
            # Check for camera make/model indicating a real shot
            make = metadata.get("Image Make", "")
            model = metadata.get("Image Model", "")
            if make or model:
                meta_score = 0.0
                meta_status = "success"
                meta_details = f"Contains authentic camera signatures: {make} {model}."
            else:
                meta_score = 0.2
                meta_status = "neutral"
                meta_details = "Contains generic EXIF metadata but no specific camera identifiers."
    else:
        meta_score = 0.5
        meta_status = "warning"
        meta_details = "All EXIF metadata has been stripped. This is common for social media sharing but untraceable."

    # 3. File Header & Extension Check
    _, ext = os.path.splitext(filename.lower())
    ext = ext.replace(".", "")
    
    # Map extension to format names
    ext_map = {
        "jpg": "JPEG",
        "jpeg": "JPEG",
        "png": "PNG",
        "gif": "GIF",
        "bmp": "BMP",
        "webp": "WEBP"
    }
    
    expected_format = ext_map.get(ext, "")
    extension_mismatch = False
    
    if expected_format and format_detected and expected_format != format_detected:
        extension_mismatch = True
        
    if extension_mismatch:
        struct_score = 1.0
        struct_status = "warning"
        struct_details = f"Extension spoofing detected: named as '{ext.upper()}' but actual byte header is '{format_detected}'."
    else:
        struct_score = 0.0
        struct_status = "success"
        struct_details = f"File extension matches header signature ({format_detected})."

    # 4. Image Manipulation Signal (Error Level Analysis)
    ela_score = 0.0
    ela_status = "neutral"
    ela_details = "Manipulation detection not performed."
    
    if manipulation_detection:
        ela_score = manipulation_detection.get("ela_score", 0.0)
        ela_status = manipulation_detection.get("status", "neutral")
        ela_details = manipulation_detection.get("verdict", "")

    # 5. Consolidated Verdict Heuristics
    has_camera = (meta_status == "success")
    is_ela_clean = (ela_status == "success")
    
    if extension_mismatch:
        verdict = "Suspicious / Manipulated"
        confidence = "High"
        summary_text = "Critical file format mismatch. The file extension has been altered to disguise the actual format header."
    elif has_camera and ai_score >= 0.75:
        # Conflict: Authentic camera signature vs AI score
        verdict = "Uncertain"
        confidence = "Low"
        summary_text = "Neural analysis flagged synthetic-like features, but the presence of authentic camera EXIF metadata strongly suggests the image is a real photograph."
    elif is_ela_clean and ai_score >= 0.75 and meta_status == "neutral":
        # Conflict: AI flagged but no edit signs and clean ELA
        verdict = "Uncertain"
        confidence = "Moderate"
        summary_text = "Neural patterns show synthetic similarities, but uniform compression levels and clean metadata present conflicting indicators."
    elif ela_status == "warning":
        verdict = "Suspicious / Manipulated"
        confidence = "High"
        summary_text = "Error Level Analysis detected significant localized compression discrepancies, indicating selective pixel editing or splicing."
    elif ai_score >= 0.75:
        # Real photos with text/compression can score high (up to 0.998), but actual AI images
        # score extremely close to 1.0 (>= 0.999).
        if ai_score < 0.999 and (is_ela_clean or ela_status == "neutral"):
            verdict = "Uncertain"
            confidence = "Moderate"
            summary_text = f"Neural analysis detected synthetic-like patterns ({ai_score*100:.1f}% probability), but uniform ELA compression suggests this may be a false positive (common in social media uploads containing high-contrast text)."
        else:
            verdict = "Likely AI-generated"
            confidence = "High" if ai_score >= 0.99 else "Moderate"
            if meta_status == "warning":
                summary_text = f"Neural analysis strongly indicates synthetic patterns ({ai_score*100:.1f}% probability). Note: Heavy web compression or skin-smoothing filters can trigger false neural positives on authentic photos."
            else:
                summary_text = "Visual feature analysis strongly indicates synthetic patterns typical of AI generators."
    elif meta_score == 1.0:
        verdict = "Suspicious / Manipulated"
        confidence = "High"
        summary_text = "Metadata software signatures confirm the image was modified using editing or graphic tools."
    elif ai_score <= 0.25:
        verdict = "Likely human-created"
        if meta_score == 0.0:
            confidence = "High"
            summary_text = "Verified camera EXIF indicators match the human-created pixel distribution signature."
        else:
            confidence = "Moderate"
            summary_text = "Pixel patterns indicate natural creation, although metadata is missing or stripped."
    else:
        verdict = "Uncertain"
        confidence = "Moderate"
        summary_text = "AI classification is inconclusive and metadata contains no clear camera or editing footprint."

    # Combined score (AI: 40%, Metadata: 20%, ELA: 30%, Header: 10%)
    ela_normalized = min(ela_score / 5.0, 1.0)
    score = (ai_score * 0.4) + (meta_score * 0.2) + (ela_normalized * 0.3) + (struct_score * 0.1)
    
    # Dampen risk score if genuine camera EXIF signatures are present
    if has_camera:
        score = max(0.0, score - 0.3)
    
    return {
        "verdict": verdict,
        "confidence": confidence,
        "summary_text": summary_text,
        "score": round(score, 4),
        "signals": {
            "ai_generation": {
                "score": round(ai_score, 4),
                "status": ai_status,
                "details": ai_details
            },
            "metadata_integrity": {
                "score": round(meta_score, 4),
                "status": meta_status,
                "details": meta_details
            },
            "file_structure": {
                "score": round(struct_score, 4),
                "status": struct_status,
                "details": struct_details
            },
            "pixel_manipulation": {
                "score": round(ela_score, 4),
                "status": ela_status,
                "details": ela_details
            }
        }
    }
