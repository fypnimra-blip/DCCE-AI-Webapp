import streamlit as st
import os
import tempfile
import time
import json
import uuid
from PIL import Image
import subprocess
import sys
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="DCNE Demo",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS to remove all top spacing
st.markdown("""
<style>
    /* Remove all top spacing from Streamlit */
    .stApp {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .main .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        margin-top: 0 !important;
    }
    
    section[data-testid="stSidebar"] {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    
    .css-1d391kg {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    
    /* Remove any default browser margins */
    body {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Target the main content wrapper */
    .main .block-container > div:first-child {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 1rem;
        margin-top: 0; /* Moved to 0 for top positioning */
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .upload-section {
        padding: 1rem; /* Reduced from 2rem */
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1rem; /* Reduced from 2rem */
        /* Removed: border: 2px dashed #dee2e6; */
        /* Removed: background-color: #f8f9fa; */
    }
    
    .progress-container {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .progress-step {
        display: flex;
        align-items: center;
        margin: 1rem 0;
        padding: 1rem;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .progress-step.active {
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .step-icon {
        font-size: 1.5rem;
        margin-right: 1rem;
        width: 40px;
        text-align: center;
    }
    
    .step-text {
        font-size: 1.1rem;
        font-weight: 500;
    }
    
    .step-time {
        margin-left: auto;
        font-size: 0.9rem;
        color: #666;
        font-style: italic;
    }
    
    .metric-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        margin: 0.5rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
    }
    
    .duplicate-item {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 0.5rem;
        margin: 0.25rem 0;
    }
    
    .debug-info {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 5px;
        padding: 1rem;
        margin: 0.5rem 0;
        font-family: monospace;
        font-size: 0.8rem;
        max-height: 200px;
        overflow-y: auto;
    }
    
    /* Move sidebar and main content to the very top */
    .css-1d391kg {
        padding-top: 0 !important;
    }
    
    .main .block-container {
        padding-top: 0 !important;
    }
    
    /* Remove any default margins from Streamlit */
    .stApp {
        margin-top: 0 !important;
    }
    
    /* Adjust sidebar title positioning */
    .css-1d391kg .css-1lcbmhc {
        padding-top: 0.5rem !important;
    }
    
    /* Target Streamlit's main container */
    .main .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    
    /* Target the sidebar container */
    section[data-testid="stSidebar"] {
        padding-top: 0 !important;
    }
    
    /* Target the main content area */
    .main .block-container > div {
        padding-top: 0 !important;
    }
    
    /* Remove top margin from the app container */
    .stApp > div {
        margin-top: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

def create_temp_directory():
    """Create a temporary directory for processing"""
    # Create temp directory in a deployment-friendly location
    
    # For deployment: Use system temp directory
    if os.environ.get('DEPLOYMENT_MODE'):
        # Production deployment
        temp_dir = os.path.join(tempfile.gettempdir(), "hexagon_detection", f"hexagon_detection_{uuid.uuid4().hex[:8]}")
    else:
        # Development mode - use project folder
        temp_dir = os.path.join(os.getcwd(), "temp-directory", f"hexagon_detection_{uuid.uuid4().hex[:8]}")
    
    os.makedirs(temp_dir, exist_ok=True)
    print(f"🔍 Temporary directory created: {temp_dir}")
    return temp_dir

def run_dcne_detection(image_path, temp_dir):
    """Run DCNE detection on the uploaded image"""
    try:
        # Run DCNE detection - it will create output in the main output directory
        cmd = [
            sys.executable, "DCNE.py",
            "--image", image_path,
            "--upscale", "4.0",
            "--threshold", "0.5"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            # Find the created output files in a deployment-friendly location
            image_name = Path(image_path).stem
            
            # For deployment: Use system temp directory for outputs
            if os.environ.get('DEPLOYMENT_MODE'):
                # Production deployment
                output_folder = os.path.join(tempfile.gettempdir(), "hexagon_output", image_name)
            else:
                # Development mode - use project folder
                output_folder = os.path.join("output", image_name)
            
            if os.path.exists(output_folder):
                annotated_image = os.path.join(output_folder, f"annotated_{image_name}.jpg")
                detection_json = os.path.join(output_folder, f"annotated_{image_name}_detections.json")
                
                # Check if files actually exist
                if os.path.exists(annotated_image) and os.path.exists(detection_json):
                    return {
                        'success': True,
                        'annotated_image': annotated_image,
                        'detection_json': detection_json,
                        'output_folder': output_folder
                    }
                else:
                    return {'success': False, 'error': f"Output files not found. Expected: {annotated_image}, {detection_json}"}
            else:
                return {'success': False, 'error': f"Output folder not found: {output_folder}"}
        
        # If we get here, the command failed
        error_msg = result.stderr if result.stderr else result.stdout
        return {'success': False, 'error': f"Command failed with return code {result.returncode}: {error_msg}"}
        
    except Exception as e:
        return {'success': False, 'error': f"Exception occurred: {str(e)}"}

def run_hexagon_extraction(image_path, temp_dir):
    """Run hexagon extraction"""
    try:
        # Create extraction directory in temp_dir
        extraction_dir = os.path.join(temp_dir, "extracted_hexagons")
        os.makedirs(extraction_dir, exist_ok=True)
        
        # Run extraction
        cmd = [
            sys.executable, "extract_hexagons.py",
            image_path,
            "--output", extraction_dir,
            "--threshold", "0.70"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            # Find the extracted hexagons folder
            image_name = Path(image_path).stem
            hexagons_folder = os.path.join(extraction_dir, image_name)
            
            if os.path.exists(hexagons_folder):
                hexagon_files = [f for f in os.listdir(hexagons_folder) if f.endswith('.png')]
                return {
                    'success': True,
                    'hexagons_folder': hexagons_folder,
                    'hexagon_count': len(hexagon_files)
                }
            else:
                return {'success': False, 'error': f"Hexagons folder not found: {hexagons_folder}"}
        
        # If we get here, the command failed
        error_msg = result.stderr if result.stderr else result.stdout
        return {'success': False, 'error': f"Command failed with return code {result.returncode}: {error_msg}"}
        
    except Exception as e:
        return {'success': False, 'error': f"Exception occurred: {str(e)}"}

def run_hexagon_validation(hexagons_folder, temp_dir):
    """Run GPT-4 validation"""
    try:
        # Get the folder name to determine the expected file prefix
        folder_name = os.path.basename(hexagons_folder)
        
        # The extract_hexagon_info.py script creates files in the hexagon folder
        # Use the exact output path that will be created
        validation_json = os.path.join(hexagons_folder, f"hexagon_validation_{folder_name}.json")
        true_hexagons_json = os.path.join(hexagons_folder, f"hexagon_validation_{folder_name}_true_hexagons.json")
        
        # Run validation - use the exact path that works
        cmd = [
            sys.executable, "extract_hexagon_info.py",
            hexagons_folder,
            "--output", validation_json
        ]
        
        # Store debug info for sidebar
        debug_info = {
            'command': ' '.join(cmd),
            'return_code': None,
            'stdout': None,
            'stderr': None,
            'created_files': None
        }
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
        
        # Update debug info
        debug_info['return_code'] = result.returncode
        debug_info['stdout'] = result.stdout
        debug_info['stderr'] = result.stderr
        
        if result.returncode == 0:
            # The script creates both the main validation file and the true hexagons file
            # Let's check what files were actually created
            created_files = os.listdir(hexagons_folder)
            debug_info['created_files'] = created_files
            
            # Look for the true hexagons file with the correct naming pattern
            true_hexagons_file = None
            for file in created_files:
                if "true_hexagons" in file and file.endswith('.json'):
                    true_hexagons_file = os.path.join(hexagons_folder, file)
                    break
            
            if true_hexagons_file and os.path.exists(true_hexagons_file):
                # Load true hexagons data
                with open(true_hexagons_file, 'r', encoding='utf-8') as f:
                    true_hexagons = json.load(f)
                
                return {
                    'success': True,
                    'validation_json': validation_json,
                    'true_hexagons_json': true_hexagons_file,
                    'true_hexagons': true_hexagons,
                    'true_count': len(true_hexagons),
                    'debug_info': debug_info
                }
            else:
                return {'success': False, 'error': f"True hexagons file not found. Available files: {created_files}", 'debug_info': debug_info}
        
        # If we get here, the command failed
        error_msg = result.stderr if result.stderr else result.stdout
        return {'success': False, 'error': f"Command failed with return code {result.returncode}: {error_msg}", 'debug_info': debug_info}
        
    except Exception as e:
        return {'success': False, 'error': f"Exception occurred: {str(e)}"}

def run_enhanced_mapping(original_image, true_hexagons_json, detection_json, temp_dir):
    """Run enhanced hexagon mapping"""
    try:
        # Create mapping output directory
        mapping_dir = os.path.join(temp_dir, "mapping")
        os.makedirs(mapping_dir, exist_ok=True)
        
        # Run enhanced mapping
        cmd = [
            sys.executable, "enhanced_hexagon_processor.py",
            original_image,
            true_hexagons_json,
            "--detection-json", detection_json,
            "--output", os.path.join(mapping_dir, "final_mapped_image.jpg")
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            mapped_image = os.path.join(mapping_dir, "final_mapped_image.jpg")
            duplicate_analysis = os.path.join(mapping_dir, "final_mapped_image_duplicate_analysis.json")
            
            duplicate_data = {}
            if os.path.exists(duplicate_analysis):
                with open(duplicate_analysis, 'r', encoding='utf-8') as f:
                    duplicate_data = json.load(f)
            
            return {
                'success': True,
                'mapped_image': mapped_image,
                'duplicate_analysis': duplicate_data
            }
        
        return {'success': False, 'error': result.stderr}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def main():
    # Main header
    st.markdown('<h1 class="main-header">DCNE Demo</h1>', unsafe_allow_html=True)
    
    # Sidebar with tabs
    st.sidebar.title("Pipeline Control")
    
    # Show processing status in sidebar only when processing has started or completed
    if st.session_state.get('processing_started', False) or st.session_state.get('processing_completed', False) or st.session_state.get('processing_halted', False):
        st.sidebar.markdown("### Processing Pipeline")
        
        # Define step names
        step_names = ["Detection", "Extraction", "Validation", "Mapping"]
        
        # Show only completed steps
        for i, step in enumerate(step_names):
            if i in st.session_state.get('completed_steps', []):
                # Step is completed
                if 'processing_status' in st.session_state and step in st.session_state['processing_status']:
                    time_taken = st.session_state['processing_status'][step].get('time', 0)
                    st.sidebar.success(f"{step} ({time_taken:.1f}s)")
                else:
                    st.sidebar.success(f"{step} ✓")
        
        # Show processing status
        if st.session_state.get('processing_started', False) and not st.session_state.get('processing_completed', False):
            st.sidebar.info("🔄 Processing in progress...")
    else:
        st.sidebar.info("Processing status will appear here when you start processing an image.")
    
    # File upload section
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    st.markdown("### Upload Image")
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['jpg', 'jpeg', 'png', 'bmp', 'tiff'],
        help="Upload an image containing hexagons to process"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    if uploaded_file is not None:
        # Display uploaded image
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### Uploaded Image")
            image = Image.open(uploaded_file)
            st.image(image, caption="Original Image", use_container_width=True)
        
        with col2:
            st.markdown("### 📋 Image Information")
            st.write(f"**File Name:** {uploaded_file.name}")
            st.write(f"**File Size:** {uploaded_file.size / 1024:.1f} KB")
            st.write(f"**Image Size:** {image.size[0]} x {image.size[1]} pixels")
            st.write(f"**Format:** {image.format}")
        
        # Process button with loading state
        if 'processing_started' not in st.session_state:
            st.session_state.processing_started = False
            
        if 'processing_completed' not in st.session_state:
            st.session_state.processing_completed = False
            
        if 'processing_halted' not in st.session_state:
            st.session_state.processing_halted = False
            
        if 'current_step' not in st.session_state:
            st.session_state.current_step = 0  # 0=Detection, 1=Extraction, 2=Validation, 3=Mapping
            
        if 'completed_steps' not in st.session_state:
            st.session_state.completed_steps = []
        
        # Show button only if not processing, not completed, and not halted
        if not st.session_state.processing_started and not st.session_state.processing_completed and not st.session_state.processing_halted:
            if st.button("Start Processing", type="primary", use_container_width=True):
                st.session_state.processing_started = True
                st.rerun()
        
        # Show loading state when processing
        if st.session_state.processing_started and not st.session_state.processing_completed:
            # Processing message
            with st.spinner("Processing in progress..."):
                st.markdown("""
                <div style="text-align: center; padding: 20px;">
                    <div style="font-size: 24px; margin-bottom: 10px;">🔄 Processing...</div>
                    <div style="font-size: 16px; color: #666;">Please wait while we process your image</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Stop processing button below
            if st.button("⏹️ Stop Processing", type="secondary", use_container_width=True):
                st.session_state.processing_started = False
                st.session_state.processing_completed = False
                st.session_state.processing_halted = True
                st.rerun()
            
            # Initialize progress tracking
            progress_data = {
                'detection_time': 0,
                'extraction_time': 0,
                'validation_time': 0,
                'mapping_time': 0
            }
            
            # Initialize processing status if not exists
            if 'processing_status' not in st.session_state:
                st.session_state['processing_status'] = {
                    'Detection': {'completed': False, 'time': 0},
                    'Extraction': {'completed': False, 'time': 0},
                    'Validation': {'completed': False, 'time': 0},
                    'Mapping': {'completed': False, 'time': 0}
                }
            
            # Create temporary directory
            temp_dir = create_temp_directory()
            
            # Save uploaded file
            temp_image_path = os.path.join(temp_dir, uploaded_file.name)
            with open(temp_image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Check if processing was stopped
            if not st.session_state.processing_started:
                st.session_state.processing_halted = True
                st.warning("Processing was stopped")
                st.rerun()
            
            # Run all processing steps automatically
            with st.sidebar:
                # Step 1: Detection
                if 0 not in st.session_state.completed_steps:
                    with st.spinner("Making image high resolution and detecting hexagons..."):
                        start_time = time.time()
                        detection_result = run_dcne_detection(temp_image_path, temp_dir)
                        progress_data['detection_time'] = time.time() - start_time
                        
                        # Check if processing was stopped
                        if not st.session_state.processing_started:
                            st.session_state.processing_halted = True
                            st.warning("Processing was stopped during detection")
                            st.rerun()
                        
                        if detection_result['success']:
                            st.session_state['processing_status']['Detection'] = {
                                'completed': True, 
                                'time': progress_data['detection_time']
                            }
                            st.session_state.completed_steps.append(0)
                            st.success(f"Detection Complete ({progress_data['detection_time']:.1f}s)")
                        else:
                            st.error(f"Detection failed: {detection_result['error']}")
                            st.info("Debug info: Check if config.json exists and has valid API keys")
                            # Reset processing state on error
                            st.session_state.processing_started = False
                            st.session_state.processing_completed = False
                            st.session_state.processing_halted = True
                            st.rerun()
                
                # Step 2: Extraction
                if 0 in st.session_state.completed_steps and 1 not in st.session_state.completed_steps:
                    with st.spinner("Extracting individual hexagons..."):
                        start_time = time.time()
                        extraction_result = run_hexagon_extraction(temp_image_path, temp_dir)
                        progress_data['extraction_time'] = time.time() - start_time
                        
                        # Check if processing was stopped
                        if not st.session_state.processing_started:
                            st.session_state.processing_halted = True
                            st.warning("Processing was stopped during extraction")
                            st.rerun()
                        
                        if extraction_result['success']:
                            st.session_state['processing_status']['Extraction'] = {
                                'completed': True, 
                                'time': progress_data['extraction_time']
                            }
                            st.session_state.completed_steps.append(1)
                            st.success(f"Extraction Complete ({extraction_result['hexagon_count']} hexagons, {progress_data['extraction_time']:.1f}s)")
                        else:
                            st.error(f"Extraction failed: {extraction_result['error']}")
                            # Reset processing state on error
                            st.session_state.processing_started = False
                            st.session_state.processing_completed = False
                            st.session_state.processing_halted = True
                            st.rerun()
                
                # Step 3: Validation
                if 1 in st.session_state.completed_steps and 2 not in st.session_state.completed_steps:
                    with st.spinner("Validating hexagons with GPT-4..."):
                        start_time = time.time()
                        validation_result = run_hexagon_validation(extraction_result['hexagons_folder'], temp_dir)
                        progress_data['validation_time'] = time.time() - start_time
                        
                        # Check if processing was stopped
                        if not st.session_state.processing_started:
                            st.session_state.processing_halted = True
                            st.warning("Processing was stopped during validation")
                            st.rerun()
                        
                        if validation_result['success']:
                            st.session_state['processing_status']['Validation'] = {
                                'completed': True, 
                                'time': progress_data['validation_time']
                            }
                            st.session_state.completed_steps.append(2)
                            st.success(f"Validation Complete ({validation_result['true_count']} true hexagons, {progress_data['validation_time']:.1f}s)")
                        else:
                            st.error(f"Validation failed: {validation_result['error']}")
                            st.info("Debug info: Check OpenAI API key and internet connection")
                            # Reset processing state on error
                            st.session_state.processing_started = False
                            st.session_state.processing_completed = False
                            st.session_state.processing_halted = True
                            st.rerun()
                
                # Step 4: Mapping
                if 2 in st.session_state.completed_steps and 3 not in st.session_state.completed_steps:
                    with st.spinner("Mapping and counting duplicates..."):
                        start_time = time.time()
                        mapping_result = run_enhanced_mapping(
                            temp_image_path,
                            validation_result['true_hexagons_json'],
                            detection_result['detection_json'],
                            temp_dir
                        )
                        progress_data['mapping_time'] = time.time() - start_time
                        
                        # Check if processing was stopped
                        if not st.session_state.processing_started:
                            st.session_state.processing_halted = True
                            st.warning("Processing was stopped during mapping")
                            st.rerun()
                        
                        if mapping_result['success']:
                            st.session_state['processing_status']['Mapping'] = {
                                'completed': True, 
                                'time': progress_data['mapping_time']
                            }
                            st.session_state.completed_steps.append(3)
                            st.success(f"Mapping Complete ({progress_data['mapping_time']:.1f}s)")
                        else:
                            st.error(f"Mapping failed: {mapping_result['error']}")
                            # Reset processing state on error
                            st.session_state.processing_started = False
                            st.session_state.processing_completed = False
                            st.session_state.processing_halted = True
                            st.rerun()
            
            # Check if all steps are completed
            if len(st.session_state.completed_steps) == 4:
                # Mark processing as completed
                st.session_state.processing_completed = True
                st.session_state.processing_started = False
                
                # Show completion message in sidebar
                st.sidebar.success("✅ Processing completed successfully!")
                
                # Store results in session state for display
                st.session_state['processing_results'] = {
                    'detection_result': detection_result,
                    'extraction_result': extraction_result,
                    'validation_result': validation_result,
                    'mapping_result': mapping_result,
                    'progress_data': progress_data,
                    'temp_dir': temp_dir
                }
                
                st.rerun()
        
        # Show halted state when processing was stopped
        elif st.session_state.processing_halted:
            st.markdown("""
            <div style="text-align: center; padding: 20px; background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 10px; margin: 20px 0;">
                <div style="font-size: 24px; margin-bottom: 10px;">⏸️ Processing Halted</div>
                <div style="font-size: 16px; color: #666;">Processing was stopped by the user. You can start processing again or upload a new image.</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Reset button to start over
            if st.button("🔄 Start Processing Again", type="primary", use_container_width=True):
                st.session_state.processing_halted = False
                st.session_state.processing_started = True
                st.session_state.processing_completed = False
                st.rerun()
        
        # Show results when processing is completed
        elif st.session_state.processing_completed and 'processing_results' in st.session_state:
            results = st.session_state['processing_results']
            
            # Results section
            st.markdown("### Results Summary")
            
            # Metrics - Only True Hexagons and Processing Time
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-value">{results['validation_result']['true_count']}</div>
                    <div class="metric-label">True Hexagons</div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col2:
                total_time = sum(results['progress_data'].values())
                st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-value">{total_time:.1f}s</div>
                    <div class="metric-label">Processing Time</div>
                </div>
                ''', unsafe_allow_html=True)
            
            # Duplicate analysis - show all instances including unique ones
            if results['mapping_result'].get('duplicate_analysis'):
                st.markdown("### Instance Analysis")
                duplicates = results['mapping_result']['duplicate_analysis'].get('duplicates', {})
                all_instances = results['mapping_result']['duplicate_analysis'].get('all_instances', {})
                
                if all_instances:
                    for key, info in all_instances.items():
                        count = info.get('count', 1)
                        if count > 1:
                            # Multiple instances - show as duplicate
                            st.markdown(f'''
                            <div class="duplicate-item">
                                <strong>{key}</strong>: {count} instances
                            </div>
                            ''', unsafe_allow_html=True)
                        else:
                            # Single instance - show as unique
                            st.markdown(f'''
                            <div class="duplicate-item" style="background-color: #d4edda; border-color: #c3e6cb;">
                                <strong>{key}</strong>: {count} instance (unique)
                            </div>
                            ''', unsafe_allow_html=True)
                elif duplicates:
                    # Fallback to duplicates if all_instances not available
                    for key, info in duplicates.items():
                        st.markdown(f'''
                        <div class="duplicate-item">
                            <strong>{key}</strong>: {info['count']} instances
                        </div>
                        ''', unsafe_allow_html=True)
                else:
                    st.info("No instances found!")
            
            # Display final mapped image
            if results['mapping_result']['success'] and os.path.exists(results['mapping_result']['mapped_image']):
                st.markdown("### Final Result")
                final_image = Image.open(results['mapping_result']['mapped_image'])
                st.image(final_image, caption="Mapped True Hexagons", use_container_width=True)
            
            # Store temp directory info for debug tab
            st.session_state['temp_dir_info'] = {
                'temp_dir': results['temp_dir'],
                'file_count': len(os.listdir(results['temp_dir'])) if os.path.exists(results['temp_dir']) else 0
            }

if __name__ == "__main__":
    main()
