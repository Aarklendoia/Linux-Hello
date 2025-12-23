use anyhow::{Result, Context};
use ndarray::{Array1, Array2};
use std::sync::{Arc, Mutex};
use crate::config::Config;

/// Embeddings handler using ONNX Runtime
pub struct Embeddings {
    // In a real implementation, this would hold the ONNX session
    // For now, placeholder to avoid ONNX dependency issues
    threshold: f32,
}

impl Embeddings {
    pub fn new(config: &Config) -> Result<Self> {
        log::info!(
            "Initializing ONNX embeddings from: {:?}",
            config.recognition_model_path()
        );

        // TODO: Load actual ONNX model
        // let session = ort::Session::builder()?
        //     .commit_from_file(config.recognition_model_path())?;

        Ok(Self {
            threshold: config.threshold,
        })
    }

    /// Compute embedding from raw image data (placeholder)
    pub fn compute_embedding(&self, _image_data: &[u8]) -> Result<Array1<f32>> {
        // TODO: Call ONNX model
        // For now, return a dummy embedding
        Ok(Array1::zeros(512))
    }

    /// Compute cosine similarity between two embeddings
    pub fn cosine_similarity(a: &Array1<f32>, b: &Array1<f32>) -> f32 {
        let dot_product = a.dot(b);
        
        let norm_a = a.iter().map(|x| x * x).sum::<f32>().sqrt();
        let norm_b = b.iter().map(|x| x * x).sum::<f32>().sqrt();

        if norm_a == 0.0 || norm_b == 0.0 {
            0.0
        } else {
            dot_product / (norm_a * norm_b)
        }
    }

    pub fn matches_threshold(&self, similarity: f32) -> bool {
        similarity >= self.threshold
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_cosine_similarity() {
        let a = Array1::from(vec![1.0, 0.0, 0.0]);
        let b = Array1::from(vec![1.0, 0.0, 0.0]);
        let sim = Embeddings::cosine_similarity(&a, &b);
        assert!((sim - 1.0).abs() < 0.001);
    }

    #[test]
    fn test_threshold_matching() {
        let emb = Embeddings {
            threshold: 0.35,
        };
        assert!(emb.matches_threshold(0.5));
        assert!(!emb.matches_threshold(0.2));
    }
}
