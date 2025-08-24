import os
import tempfile
import uuid
from pathlib import Path

def test_deployment_config():
    """Test deployment configuration and show file storage locations"""
    
    print("🔧 Testing Deployment Configuration")
    print("=" * 50)
    
    # Test current environment
    deployment_mode = os.environ.get('DEPLOYMENT_MODE', 'development')
    storage_type = os.environ.get('STORAGE_TYPE', 'local')
    
    print(f"📋 Current Configuration:")
    print(f"   DEPLOYMENT_MODE: {deployment_mode}")
    print(f"   STORAGE_TYPE: {storage_type}")
    print()
    
    # Test temp directory creation
    session_id = f"hexagon_detection_{uuid.uuid4().hex[:8]}"
    
    if deployment_mode == 'production':
        if storage_type == 'local':
            temp_dir = os.path.join(tempfile.gettempdir(), "hexagon_detection", session_id)
        elif storage_type == 'shared':
            temp_dir = os.path.join("/shared/uploads", "hexagon_detection", session_id)
        else:
            temp_dir = os.path.join(tempfile.gettempdir(), "hexagon_detection", session_id)
    else:
        temp_dir = os.path.join(os.getcwd(), "temp-directory", session_id)
    
    # Create directory
    os.makedirs(temp_dir, exist_ok=True)
    
    print(f"📁 File Storage Locations:")
    print(f"   Temporary Directory: {temp_dir}")
    
    # Test output directory
    image_name = "test_image"
    if deployment_mode == 'production':
        if storage_type == 'local':
            output_dir = os.path.join(tempfile.gettempdir(), "hexagon_output", session_id, image_name)
        elif storage_type == 'shared':
            output_dir = os.path.join("/shared/results", "hexagon_output", session_id, image_name)
        else:
            output_dir = os.path.join(tempfile.gettempdir(), "hexagon_output", session_id, image_name)
    else:
        output_dir = os.path.join("output", image_name)
    
    os.makedirs(output_dir, exist_ok=True)
    print(f"   Output Directory: {output_dir}")
    print()
    
    # Create test files
    test_temp_file = os.path.join(temp_dir, "test_temp.txt")
    test_output_file = os.path.join(output_dir, "test_output.txt")
    
    with open(test_temp_file, 'w') as f:
        f.write("Test temporary file")
    
    with open(test_output_file, 'w') as f:
        f.write("Test output file")
    
    print(f"✅ Test Files Created:")
    print(f"   Temp file: {test_temp_file}")
    print(f"   Output file: {test_output_file}")
    print()
    
    # Show system temp directory
    print(f"🌐 System Information:")
    print(f"   System Temp Directory: {tempfile.gettempdir()}")
    print(f"   Current Working Directory: {os.getcwd()}")
    print()
    
    # Show how to access files
    print(f"🔍 How to Access Files:")
    if deployment_mode == 'production':
        print(f"   Windows: Open File Explorer and navigate to:")
        print(f"   {tempfile.gettempdir()}")
        print(f"   Linux/Mac: Use terminal command:")
        print(f"   ls {tempfile.gettempdir()}/hexagon_detection/")
    else:
        print(f"   Development mode: Files are in project directory")
        print(f"   {os.path.join(os.getcwd(), 'temp-directory')}")
    
    print()
    print("🎯 Test completed! Check the directories above to see the test files.")

if __name__ == "__main__":
    test_deployment_config()
