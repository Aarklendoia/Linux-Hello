#!/usr/bin/env python3
"""
Export InsightFace recognition model to ONNX format for Rust daemon.

This script extracts the face recognition model from InsightFace
and saves it as ONNX for use with ort-rs in the Rust daemon.
"""

import os
import sys
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def export_recognition_model():
    """Export InsightFace recognition model to ONNX."""
    try:
        import insightface
        import onnx
        from onnx import optimizer
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        logger.error("Install with: pip install insightface onnx")
        return False

    logger.info("Loading InsightFace model...")
    
    try:
        # Load the face analysis app
        app = insightface.app.FaceAnalysis(
            name='buffalo_l',  # Use buffalo_l model (good balance)
            providers=['CPUProvider']
        )
        app.prepare(ctx_id=-1)
        
        logger.info("InsightFace model loaded successfully")
        
        # Get the recognition model
        rec_model = app.models['recognition']
        logger.info(f"Recognition model: {rec_model}")
        
        # Export to ONNX
        output_dir = Path("/opt/linux-hello/models")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / "recognition.onnx"
        
        logger.info(f"Exporting recognition model to {output_path}...")
        
        # Try to export using torch/mxnet native export
        if hasattr(rec_model, 'model'):
            model = rec_model.model
            
            # Check if it's a PyTorch model
            if hasattr(model, 'state_dict'):
                import torch
                import torch.onnx
                
                logger.info("Detected PyTorch model, exporting...")
                
                # Create dummy input (512x512 RGB image)
                dummy_input = torch.randn(1, 3, 112, 112)
                
                torch.onnx.export(
                    model,
                    dummy_input,
                    str(output_path),
                    opset_version=12,
                    input_names=['images'],
                    output_names=['embeddings'],
                    dynamic_axes={
                        'images': {0: 'batch_size'},
                        'embeddings': {0: 'batch_size'}
                    },
                    verbose=False
                )
                
                logger.info(f"✓ Model exported to {output_path}")
                
                # Verify the ONNX model
                onnx_model = onnx.load(str(output_path))
                onnx.checker.check_model(onnx_model)
                logger.info("✓ ONNX model validation passed")
                
                return True
            else:
                logger.warning("Model doesn't appear to be PyTorch")
                return False
        else:
            logger.warning("Could not access model from FaceAnalysis")
            return False
            
    except Exception as e:
        logger.error(f"Export failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def export_detection_model():
    """Export face detection model (optional, for faster detection)."""
    try:
        import insightface
    except ImportError:
        logger.warning("InsightFace not available for detection model")
        return False

    logger.info("Loading face detection model (optional)...")
    
    try:
        app = insightface.app.FaceAnalysis(
            name='buffalo_l',
            providers=['CPUProvider']
        )
        app.prepare(ctx_id=-1)
        
        det_model = app.models['detection']
        logger.info(f"Detection model: {det_model}")
        
        output_dir = Path("/opt/linux-hello/models")
        output_path = output_dir / "detection.onnx"
        
        logger.info(f"Exporting detection model to {output_path}...")
        
        # Detection model export (if supported)
        # This is model-dependent and might not always be available
        logger.info("⚠ Detection model export not fully implemented (use face_api or similar)")
        
        return True
        
    except Exception as e:
        logger.warning(f"Detection model export not available: {e}")
        return False

def main():
    logger.info("=" * 60)
    logger.info("Linux Hello - ONNX Model Export Utility")
    logger.info("=" * 60)
    
    # Check permissions
    output_dir = Path("/opt/linux-hello/models")
    if not output_dir.exists():
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created {output_dir}")
        except PermissionError:
            logger.error(f"Permission denied: cannot create {output_dir}")
            logger.info("Try: sudo mkdir -p /opt/linux-hello/models")
            logger.info("     sudo chown $USER:$USER /opt/linux-hello/models")
            return False
    
    # Export recognition model
    logger.info("\n[1/2] Exporting recognition model...")
    if export_recognition_model():
        logger.info("✓ Recognition model exported")
    else:
        logger.error("✗ Recognition model export failed")
        return False
    
    # Export detection model (optional)
    logger.info("\n[2/2] Exporting detection model (optional)...")
    export_detection_model()
    
    logger.info("\n" + "=" * 60)
    logger.info("Export complete!")
    logger.info("Models location: /opt/linux-hello/models/")
    logger.info("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
