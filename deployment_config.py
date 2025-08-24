import os
import tempfile
from pathlib import Path

class DeploymentConfig:
    """
    Configuration for deployment environments
    """
    
    def __init__(self):
        self.deployment_mode = os.environ.get('DEPLOYMENT_MODE', 'development')
        self.storage_type = os.environ.get('STORAGE_TYPE', 'local')
        
    def get_temp_directory(self, session_id: str) -> str:
        """Get temporary directory for processing"""
        if self.deployment_mode == 'production':
            if self.storage_type == 'local':
                # Local server storage
                temp_dir = os.path.join(tempfile.gettempdir(), "hexagon_detection", session_id)
            elif self.storage_type == 'shared':
                # Shared network storage
                temp_dir = os.path.join("/shared/uploads", "hexagon_detection", session_id)
            else:
                # Default to system temp
                temp_dir = os.path.join(tempfile.gettempdir(), "hexagon_detection", session_id)
        else:
            # Development mode
            temp_dir = os.path.join(os.getcwd(), "temp-directory", session_id)
        
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir
    
    def get_output_directory(self, session_id: str, image_name: str) -> str:
        """Get output directory for results"""
        if self.deployment_mode == 'production':
            if self.storage_type == 'local':
                # Local server storage
                output_dir = os.path.join(tempfile.gettempdir(), "hexagon_output", session_id, image_name)
            elif self.storage_type == 'shared':
                # Shared network storage
                output_dir = os.path.join("/shared/results", "hexagon_output", session_id, image_name)
            else:
                # Default to system temp
                output_dir = os.path.join(tempfile.gettempdir(), "hexagon_output", session_id, image_name)
        else:
            # Development mode
            output_dir = os.path.join("output", image_name)
        
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """Clean up old temporary files"""
        import time
        import shutil
        
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        # Clean up temp directories
        temp_dirs = [
            os.path.join(tempfile.gettempdir(), "hexagon_detection"),
            os.path.join(tempfile.gettempdir(), "hexagon_output")
        ]
        
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                for item in os.listdir(temp_dir):
                    item_path = os.path.join(temp_dir, item)
                    if os.path.isdir(item_path):
                        # Check if directory is old
                        if current_time - os.path.getctime(item_path) > max_age_seconds:
                            try:
                                shutil.rmtree(item_path)
                                print(f"Cleaned up old directory: {item_path}")
                            except Exception as e:
                                print(f"Failed to clean up {item_path}: {e}")

# Global configuration instance
config = DeploymentConfig()
