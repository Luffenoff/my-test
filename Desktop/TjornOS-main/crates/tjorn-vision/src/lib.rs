pub mod camera;
pub mod detection;
pub mod recognition;
pub mod tracking;
pub mod processing;

use std::sync::Arc;
use anyhow::Result;

pub struct VisionSystem {
    camera_manager: Arc<camera::CameraManager>,
    object_detector: Arc<detection::ObjectDetector>,
    face_recognizer: Arc<recognition::FaceRecognizer>,
    motion_tracker: Arc<tracking::MotionTracker>,
}

impl VisionSystem {
    pub async fn new() -> Result<Self> {
        Ok(Self {
            camera_manager: Arc::new(camera::CameraManager::new()?),
            object_detector: Arc::new(detection::ObjectDetector::new()?),
            face_recognizer: Arc::new(recognition::FaceRecognizer::new()?),
            motion_tracker: Arc::new(tracking::MotionTracker::new()?),
        })
    }

    pub async fn process_frame(&self, frame: &[u8]) -> Result<VisionResult> {
        let objects = self.object_detector.detect(frame).await?;
        let faces = self.face_recognizer.recognize(frame).await?;
        let motion = self.motion_tracker.track(frame).await?;
        
        Ok(VisionResult {
            objects,
            faces,
            motion,
        })
    }
}

#[derive(Debug)]
pub struct VisionResult {
    pub objects: Vec<DetectedObject>,
    pub faces: Vec<RecognizedFace>,
    pub motion: MotionData,
}

pub fn init() {
    println!("Initializing {}", "tjorn-vision");
}
