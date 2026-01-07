//! Rendering optimizations - frame caching and lazy bounding box

/// Frame cache for reducing redundant calculations
#[derive(Debug, Clone)]
pub struct FrameCache {
    /// Last rendered frame data (cached)
    pub cached_frame_id: Option<u32>,
    /// Whether cache is valid
    pub is_valid: bool,
}

impl FrameCache {
    /// Create a new frame cache
    pub fn new() -> Self {
        Self {
            cached_frame_id: None,
            is_valid: false,
        }
    }

    /// Check if cache is valid for a given frame
    pub fn is_valid_for(&self, frame_id: u32) -> bool {
        self.is_valid && self.cached_frame_id == Some(frame_id)
    }

    /// Mark cache as valid for a frame
    pub fn mark_valid(&mut self, frame_id: u32) {
        self.cached_frame_id = Some(frame_id);
        self.is_valid = true;
    }

    /// Invalidate cache (new frame received)
    pub fn invalidate(&mut self) {
        self.is_valid = false;
    }
}

impl Default for FrameCache {
    fn default() -> Self {
        Self::new()
    }
}

/// Bounding box cache
#[derive(Debug, Clone, Copy)]
pub struct BoundingBoxCache {
    /// Cached bounding box (x, y, width, height)
    pub bbox: Option<(u32, u32, u32, u32)>,
    /// Whether to skip drawing
    pub should_draw: bool,
    /// Confidence threshold (0.0-1.0)
    pub confidence_threshold: f32,
}

impl BoundingBoxCache {
    /// Create a new bounding box cache with default threshold
    pub fn new() -> Self {
        Self {
            bbox: None,
            should_draw: false,
            confidence_threshold: 0.7,
        }
    }

    /// Update cache with new detection data
    pub fn update(&mut self, detected: bool, confidence: f32) {
        // Only draw if detected and confidence is above threshold
        self.should_draw = detected && confidence >= self.confidence_threshold;
    }

    /// Check if bounding box should be drawn
    pub fn should_draw_bbox(&self) -> bool {
        self.should_draw
    }
}

impl Default for BoundingBoxCache {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_frame_cache_creation() {
        let cache = FrameCache::new();
        assert!(!cache.is_valid);
        assert_eq!(cache.cached_frame_id, None);
    }

    #[test]
    fn test_frame_cache_validation() {
        let mut cache = FrameCache::new();
        
        cache.mark_valid(1);
        assert!(cache.is_valid);
        assert!(cache.is_valid_for(1));
        assert!(!cache.is_valid_for(2));
    }

    #[test]
    fn test_frame_cache_invalidation() {
        let mut cache = FrameCache::new();
        cache.mark_valid(1);
        
        cache.invalidate();
        assert!(!cache.is_valid);
        assert!(!cache.is_valid_for(1));
    }

    #[test]
    fn test_bbox_cache_creation() {
        let cache = BoundingBoxCache::new();
        assert!(!cache.should_draw);
        assert_eq!(cache.confidence_threshold, 0.7);
    }

    #[test]
    fn test_bbox_cache_update_threshold() {
        let mut cache = BoundingBoxCache::new();
        
        // Low confidence - should not draw
        cache.update(true, 0.5);
        assert!(!cache.should_draw_bbox());
        
        // High confidence - should draw
        cache.update(true, 0.8);
        assert!(cache.should_draw_bbox());
        
        // Not detected - should not draw
        cache.update(false, 0.9);
        assert!(!cache.should_draw_bbox());
    }

    #[test]
    fn test_bbox_cache_default() {
        let cache = BoundingBoxCache::default();
        assert!(!cache.should_draw);
    }
}
