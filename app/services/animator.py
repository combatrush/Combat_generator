import numpy as np
import torch
from PIL import Image, ImageEnhance
import cv2
from celery import Task
from transformers import AutoModel, AutoTokenizer, AutoImageProcessor
from .. import celery, db
from ..models.animation import Animation
from ..exceptions import AnimationError, ModelLoadError, RenderError, ValidationError
from typing import Tuple, List, Dict, Any, Optional, Callable
import logging

logger = logging.getLogger(__name__)

class AnimationGenerator:
    def __init__(self, model_path: Optional[str] = None):
        """Initialize the animation generator with optional model path."""
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self.image_processor = None
        self.load_models(model_path)
    
    def load_models(self, model_path: Optional[str]) -> None:
        """Load or initialize AI models for animation generation."""
        try:
            if not model_path:
                model_path = "stabilityai/stable-diffusion-2-1"
            
            logger.info(f"Loading models from {model_path}")
            self.model = AutoModel.from_pretrained(model_path)
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.image_processor = AutoImageProcessor.from_pretrained(model_path)
            
            self.model.to(self.device)
            self.model.eval()
            logger.info("Models loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load models: {str(e)}")
            raise ModelLoadError(f"Failed to load models: {str(e)}")
    
    def generate_keyframes(self, scene_data: Dict[str, Any]) -> List[np.ndarray]:
        """Generate key animation frames based on scene description."""
        try:
            if not scene_data.get('description'):
                raise ValidationError("Scene description is required")
            
            logger.info("Generating keyframes")
            # Tokenize scene description
            inputs = self.tokenizer(
                scene_data['description'],
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            ).to(self.device)
            
            # Generate frame embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)
                frame_embeddings = outputs.last_hidden_state
            
            # Convert embeddings to frames
            frames = self._embeddings_to_frames(frame_embeddings)
            logger.info(f"Generated {len(frames)} keyframes")
            
            return frames
        except ValidationError as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to generate keyframes: {str(e)}")
            raise RenderError(f"Failed to generate keyframes: {str(e)}")
    
    def interpolate_frames(self, keyframes: List[np.ndarray], fps: int) -> List[np.ndarray]:
        """Interpolate between keyframes for smooth animation."""
        try:
            if not keyframes or len(keyframes) < 2:
                raise ValidationError("At least two keyframes are required")
            
            logger.info(f"Interpolating frames at {fps} FPS")
            interpolated = []
            for i in range(len(keyframes) - 1):
                start_frame = keyframes[i]
                end_frame = keyframes[i + 1]
                
                # Calculate number of intermediate frames
                n_frames = int(fps / 2)  # 0.5 seconds between keyframes
                
                # Linear interpolation between frames
                for t in range(n_frames):
                    alpha = t / n_frames
                    frame = cv2.addWeighted(
                        start_frame,
                        1 - alpha,
                        end_frame,
                        alpha,
                        0
                    )
                    interpolated.append(frame)
            
            logger.info(f"Generated {len(interpolated)} interpolated frames")
            return interpolated
        except ValidationError as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to interpolate frames: {str(e)}")
            raise RenderError(f"Failed to interpolate frames: {str(e)}")
    
    def apply_effects(self, frames: List[np.ndarray], effects_data: Dict[str, Any]) -> List[np.ndarray]:
        """Apply post-processing effects to frames."""
        try:
            if not frames:
                raise ValidationError("No frames to process")
            
            logger.info("Applying effects")
            processed = []
            for frame in frames:
                # Convert to PIL Image for processing
                frame_pil = Image.fromarray(frame)
                
                # Apply each effect
                for effect, params in effects_data.items():
                    if effect == 'blur':
                        frame_pil = frame_pil.filter(Image.BLUR)
                    elif effect == 'brightness':
                        enhancer = ImageEnhance.Brightness(frame_pil)
                        frame_pil = enhancer.enhance(params.get('factor', 1.0))
                    # Add more effects as needed
                
                # Convert back to numpy array
                processed.append(np.array(frame_pil))
            
            logger.info(f"Applied effects to {len(processed)} frames")
            return processed
        except ValidationError as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to apply effects: {str(e)}")
            raise RenderError(f"Failed to apply effects: {str(e)}")
    
    def render_animation(
        self,
        scene_data: Dict[str, Any],
        output_path: str,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> Tuple[bool, str]:
        """Main animation rendering pipeline."""
        try:
            total_steps = 4
            current_step = 0
            
            # Generate key frames
            if progress_callback:
                progress_callback(25, "Generating keyframes")
            keyframes = self.generate_keyframes(scene_data)
            current_step += 1
            
            # Interpolate frames
            if progress_callback:
                progress_callback(50, "Interpolating frames")
            frames = self.interpolate_frames(keyframes, scene_data.get('fps', 30))
            current_step += 1
            
            # Apply effects
            if progress_callback:
                progress_callback(75, "Applying effects")
            final_frames = self.apply_effects(frames, scene_data.get('effects', {}))
            current_step += 1
            
            # Save animation
            if progress_callback:
                progress_callback(90, "Saving animation")
            self._save_animation(final_frames, output_path, scene_data)
            
            if progress_callback:
                progress_callback(100, "Complete")
            
            logger.info(f"Animation rendered successfully to {output_path}")
            return True, output_path
            
        except Exception as e:
            error_msg = f"Animation rendering failed: {str(e)}"
            logger.error(error_msg)
            if progress_callback:
                progress_callback(0, error_msg)
            raise RenderError(error_msg)
    
    def _save_animation(self, frames: List[np.ndarray], output_path: str, scene_data: Dict[str, Any]) -> None:
        """Save frames as video file."""
        try:
            if not frames:
                raise ValidationError("No frames to save")
            
            fps = scene_data.get('fps', 30)
            height, width = frames[0].shape[:2]
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            for frame in frames:
                out.write(frame)
            
            out.release()
            logger.info(f"Saved animation to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save animation: {str(e)}")
            raise RenderError(f"Failed to save animation: {str(e)}")
    
    def _embeddings_to_frames(self, embeddings: torch.Tensor) -> List[np.ndarray]:
        """Convert model embeddings to image frames."""
        try:
            # Process embeddings to generate image frames
            # This is a placeholder implementation
            frames = []
            batch_size, seq_len, hidden_dim = embeddings.shape
            
            for i in range(batch_size):
                # Generate a blank frame
                frame = np.zeros((256, 256, 3), dtype=np.uint8)
                frames.append(frame)
            
            return frames
        except Exception as e:
            logger.error(f"Failed to convert embeddings to frames: {str(e)}")
            raise RenderError(f"Failed to convert embeddings to frames: {str(e)}")


class AnimationTask(Task):
    """Celery task for handling animation generation."""
    
    def __init__(self):
        """Initialize the animation task."""
        self.animator = None
    
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Execute animation generation."""
        if not self.animator:
            self.animator = AnimationGenerator()
        return self.run(*args, **kwargs)
    
    def run(self, scene_data: Dict[str, Any], output_path: str) -> Tuple[bool, str]:
        """Run animation generation task."""
        try:
            # Get animation record
            animation_id = scene_data.get('animation_id')
            if not animation_id:
                raise ValidationError("No animation ID provided")
            
            animation = Animation.query.get(animation_id)
            if not animation:
                raise ValidationError(f"Animation {animation_id} not found")
            
            def progress_callback(progress: int, message: Optional[str] = None) -> None:
                """Update progress in both task and database."""
                self.update_progress(progress, message)
                animation.update_render_progress(progress, message)
                db.session.commit()
            
            # Run animation generation
            success, result = self.animator.render_animation(
                scene_data,
                output_path,
                progress_callback
            )
            
            if success:
                animation.status = 'completed'
                animation.output_path = result
            else:
                animation.status = 'failed'
                animation.error_message = result
            
            db.session.commit()
            return success, result
            
        except Exception as e:
            error_msg = f"Animation task failed: {str(e)}"
            logger.error(error_msg)
            if animation:
                animation.status = 'failed'
                animation.error_message = str(e)
                db.session.commit()
            raise AnimationError(error_msg)
    
    def update_progress(self, progress: int, message: Optional[str] = None) -> None:
        """Update animation progress in database."""
        self.update_state(
            state='PROGRESS',
            meta={
                'progress': progress,
                'message': message or f'Progress: {progress}%'
            }
        )


# Register Celery task
animation_task = celery.task(bind=True, base=AnimationTask)
