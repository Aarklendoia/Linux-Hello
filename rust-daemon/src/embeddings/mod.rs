use anyhow::{Result, Context};
use ndarray::{Array1, Array2};
use std::path::{Path, PathBuf};
use crate::config::Config;

/// Face recognition embedding engine
pub struct Embeddings {
    model_path: PathBuf,
    threshold: f32,
    // TODO: Add ONNX session when ort-rs is integrated
    // session: ort::Session,
}

impl Embeddings {
    pub fn new(config: &Config) -> Result<Self> {
        let model_path = config.recognition_model_path();
        
        log::info!(
            "Initializing embeddings engine from: {:?}",
            model_path
        );

        if !model_path.exists() {
            log::warn!(
                "Model not found at {:?}. Run: ./export_onnx.py",
                model_path
            );
            // Continue anyway (will fail at inference time)
        }

        // TODO: Load ONNX model when available
        // let env = ort::Environment::builder()?
        //     .with_name("linux-hello")?
        //     .build()?
        //     .into_arc();
        // let session = ort::Session::builder(&env)?
        //     .with_intra_threads(4)?
        //     .commit_from_file(&model_path)?;

        Ok(Self {
            model_path,
            threshold: config.threshold,
        })
    }

    /// Compute embedding from image data (placeholder)
    pub fn compute_embedding(&self, _image_data: &[u8]) -> Result<Array1<f32>> {
        // TODO: Call ONNX model
        // let input = ort::InputTensor::from_array(image_array)?;
        // let outputs = self.session.run(ort::inputs![input])?;
        // let embedding = outputs[0].extract_tensor()?;
        
        log::warn!("compute_embedding: ONNX not yet integrated, returning dummy embedding");
        
        // Return a dummy 512-dim embedding for now
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

    pub fn threshold(&self) -> f32 {
        self.threshold
    }

    pub fn model_path(&self) -> &Path {
        &self.model_path
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_cosine_similarity_identical() {
        let a = Array1::from(vec![1.0, 0.0, 0.0]);
        let b = Array1::from(vec![1.0, 0.0, 0.0]);
        let sim = Embeddings::cosine_similarity(&a, &b);
        assert!((sim - 1.0).abs() < 0.001, "Identical vectors should have similarity ~1.0");
    }

    #[test]
    fn test_cosine_similarity_orthogonal() {
        let a = Array1::from(vec![1.0, 0.0]);
        let b = Array1::from(vec![0.0, 1.0]);
        let sim = Embeddings::cosine_similarity(&a, &b);
        assert!(sim.abs() < 0.001, "Orthogonal vectors should have similarity ~0.0");
    }

    #[test]
    fn test_threshold_matching() {
        let emb = Embeddings {
            model_path: PathBuf::from("/tmp/dummy.onnx"),
            threshold: 0.35,
        };
        assert!(emb.matches_threshold(0.5));
        assert!(!emb.matches_threshold(0.2));
        assert!(emb.matches_threshold(0.35)); // Boundary condition
    }
}
