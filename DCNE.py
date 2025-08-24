import os
import json
import requests
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import image as mpimg
import numpy as np
from typing import List, Dict, Any
import argparse

class CustomVisionObjectDetector:
    """
    A class to interact with Azure Custom Vision Object Detection model
    """
    
    def __init__(self, prediction_key: str, prediction_endpoint: str, project_id: str, model_name: str = "DCNE_lowres"):
        """
        Initialize the Custom Vision Object Detector
        
        Args:
            prediction_key: Your Custom Vision prediction key
            prediction_endpoint: Your Custom Vision prediction endpoint
            project_id: Your Custom Vision project ID
            model_name: Name of your published model (default: "DCNE_lowres")
        """
        self.prediction_key = prediction_key
        self.prediction_endpoint = prediction_endpoint
        self.project_id = project_id
        self.model_name = model_name
        
        # Construct the prediction URL (fix double slash issue)
        endpoint = prediction_endpoint.rstrip('/')
        self.prediction_url = f"{endpoint}/customvision/v3.0/Prediction/{project_id}/detect/iterations/{model_name}/image"
        
        # Headers for the API request
        self.headers = {
            'Prediction-Key': prediction_key,
            'Content-Type': 'application/octet-stream'
        }
    
    def detect_objects_from_file(self, image_path: str) -> Dict[str, Any]:
        """
        Detect objects in an image file
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing prediction results
        """
        try:
            # Open and read the image file
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
            
            # Make the prediction request
            response = requests.post(
                self.prediction_url,
                headers=self.headers,
                data=image_data
            )
            
            # Check if the request was successful
            response.raise_for_status()
            
            # Parse the JSON response
            predictions = response.json()
            return predictions
            
        except Exception as e:
            print(f"Error detecting objects: {str(e)}")
            return None
    
    def detect_objects_from_url(self, image_url: str) -> Dict[str, Any]:
        """
        Detect objects in an image from URL
        
        Args:
            image_url: URL of the image
            
        Returns:
            Dictionary containing prediction results
        """
        try:
            # Download the image from URL
            response = requests.get(image_url)
            response.raise_for_status()
            
            # Make the prediction request
            prediction_response = requests.post(
                self.prediction_url,
                headers=self.headers,
                data=response.content
            )
            
            # Check if the request was successful
            prediction_response.raise_for_status()
            
            # Parse the JSON response
            predictions = prediction_response.json()
            return predictions
            
        except Exception as e:
            print(f"Error detecting objects from URL: {str(e)}")
            return None
    
    def visualize_detections(self, image_path: str, predictions: Dict[str, Any], 
                           output_path: str = "output/output.jpg", confidence_threshold: float = 0.5, 
                           upscale_factor: float = 2.0, enhance_image: bool = True):
        """
        Visualize object detections on the image
        
        Args:
            image_path: Path to the original image
            predictions: Prediction results from the model
            output_path: Path to save the annotated image
            confidence_threshold: Minimum confidence score to display
        """
        try:
            # Open the image
            image = Image.open(image_path)
            
            # Get original image dimensions
            original_width, original_height = image.size
            
            # Upscale the image for higher resolution
            if upscale_factor > 1.0:
                new_width = int(original_width * upscale_factor)
                new_height = int(original_height * upscale_factor)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                print(f"Upscaled image from {original_width}x{original_height} to {new_width}x{new_height}")
            
            # Enhance image for better text readability
            if enhance_image:
                # Apply sharpening filter
                image = image.filter(ImageFilter.SHARPEN)
                
                # Enhance contrast
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(1.5)  # Increase contrast by 50%
                
                # Enhance brightness slightly
                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(1.1)  # Increase brightness by 10%
                
                print("Applied image enhancement for better text readability")
            
            draw = ImageDraw.Draw(image)
            
            # Get image dimensions (after upscaling)
            img_width, img_height = image.size
            
            # Colors based on confidence level
            def get_color_by_confidence(confidence):
                if confidence >= 0.70:  # 70% or higher
                    return (0, 255, 0)  # Green
                else:
                    return (255, 0, 0)  # Red
            
            print(f"\nDetected Objects:")
            print("-" * 50)
            
            # Process each prediction
            for prediction in predictions.get('predictions', []):
                tag_name = prediction['tagName']
                probability = prediction['probability']
                bbox = prediction['boundingBox']
                
                # Only process predictions above the confidence threshold
                if probability >= confidence_threshold:
                    # Convert relative coordinates to absolute pixels
                    left = bbox['left'] * img_width
                    top = bbox['top'] * img_height
                    width = bbox['width'] * img_width
                    height = bbox['height'] * img_height
                    
                    # Get color based on confidence level
                    color = get_color_by_confidence(probability)
                    
                    # Draw bounding box with thicker lines for high resolution
                    line_width = max(3, int(3 * upscale_factor))
                    draw.rectangle(
                        [left, top, left + width, top + height],
                        outline=color,
                        width=line_width
                    )
                    
                    # No text labels - just clean bounding boxes
                    
                    # Print detection info
                    print(f"• {tag_name}: {probability:.2%} confidence")
                    print(f"  Location: ({left:.0f}, {top:.0f}) to ({left + width:.0f}, {top + height:.0f})")
            
            # Save the annotated image with high quality settings
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            
            # Save with maximum quality settings for high resolution
            image.save(output_path, 'JPEG', quality=100, optimize=False)
            
            # Save detection results to JSON file
            detection_json_path = output_path.replace('.jpg', '_detections.json')
            with open(detection_json_path, 'w') as f:
                json.dump({
                    'image_path': image_path,
                    'predictions': predictions,
                    'total_detections': len(predictions)
                }, f, indent=2)
            print(f"Detection results saved to: {detection_json_path}")
            print(f"\nAnnotated image saved as: {output_path}")
            
        except Exception as e:
            print(f"Error visualizing detections: {str(e)}")
    
    def print_detection_summary(self, predictions: Dict[str, Any], confidence_threshold: float = 0.5):
        """
        Print a summary of detected objects
        
        Args:
            predictions: Prediction results from the model
            confidence_threshold: Minimum confidence score to include
        """
        if not predictions or 'predictions' not in predictions:
            print("No predictions found.")
            return
        
        print(f"\nDetection Summary:")
        print("=" * 50)
        
        # Count objects by type
        object_counts = {}
        total_objects = 0
        
        for prediction in predictions['predictions']:
            if prediction['probability'] >= confidence_threshold:
                tag_name = prediction['tagName']
                object_counts[tag_name] = object_counts.get(tag_name, 0) + 1
                total_objects += 1
        
        if total_objects == 0:
            print("No objects detected above the confidence threshold.")
            return
        
        print(f"Total objects detected: {total_objects}")
        print("\nBreakdown by object type:")
        for obj_type, count in object_counts.items():
            print(f"• {obj_type}: {count}")
        
        print(f"\nTop predictions (confidence >= {confidence_threshold:.0%}):")
        for prediction in sorted(predictions['predictions'], 
                               key=lambda x: x['probability'], reverse=True):
            if prediction['probability'] >= confidence_threshold:
                print(f"• {prediction['tagName']}: {prediction['probability']:.2%}")

def load_config(config_file: str = "config.json") -> Dict[str, str]:
    """
    Load configuration from a JSON file
    
    Args:
        config_file: Path to the configuration file
        
    Returns:
        Dictionary containing configuration values
    """
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Configuration file '{config_file}' not found.")
        print("Please create a config.json file with your Custom Vision settings.")
        return None
    except json.JSONDecodeError:
        print(f"Error parsing configuration file '{config_file}'.")
        return None

def create_sample_config():
    """
    Create a sample configuration file
    """
    sample_config = {
        "prediction_key": "your_prediction_key_here",
        "prediction_endpoint": "https://your-resource-name.cognitiveservices.azure.com/",
        "project_id": "your_project_id_here",
        "model_name": "DCNE_lowres"
    }
    
    with open("config.json", 'w') as f:
        json.dump(sample_config, f, indent=2)
    
    print("Sample config.json file created. Please update it with your actual values.")

def find_images_in_directory(directory: str = r"C:\Users\NimraMaqbool\Downloads\good resolution custom vision\east") -> List[str]:
    """
    Find all image files in the specified directory
    
    Args:
        directory: Directory to search for images
        
    Returns:
        List of image file paths
    """
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif'}
    image_files = []
    
    try:
        for filename in os.listdir(directory):
            if any(filename.lower().endswith(ext) for ext in image_extensions):
                image_files.append(os.path.join(directory, filename))
    except Exception as e:
        print(f"Error reading directory: {str(e)}")
    
    return sorted(image_files)

def create_output_directory():
    """
    Create output directory if it doesn't exist
    """
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    return output_dir

def main():
    """
    Main function to run the object detection
    """
    parser = argparse.ArgumentParser(description='Custom Vision Hexagon Detection Tester')
    parser.add_argument('--image', '-i', help='Path to image file to test')
    parser.add_argument('--url', '-u', help='URL of image to test')
    parser.add_argument('--config', '-c', default='config.json', help='Configuration file path')
    parser.add_argument('--output', '-o', default='output/output.jpg', help='Output image path')
    parser.add_argument('--threshold', '-t', type=float, default=0.5, help='Confidence threshold (0.0-1.0)')
    parser.add_argument('--upscale', type=float, default=4.0, help='Upscale factor for higher resolution (default: 4.0)')
    parser.add_argument('--no-enhance', action='store_true', help='Disable image enhancement for better text readability')
    parser.add_argument('--create-config', action='store_true', help='Create a sample configuration file')
    parser.add_argument('--auto-detect', action='store_true', help='Automatically detect and test all images in current directory')
    
    args = parser.parse_args()
    
    # Create sample config if requested
    if args.create_config:
        create_sample_config()
        return
    
    # Create output directory
    output_dir = create_output_directory()
    
    # Load configuration
    config = load_config(args.config)
    if not config:
        return
    
    # Initialize the detector
    detector = CustomVisionObjectDetector(
        prediction_key=config['prediction_key'],
        prediction_endpoint=config['prediction_endpoint'],
        project_id=config['project_id'],
        model_name=config.get('model_name', 'DCNE_lowres')
    )
    
    # Auto-detect and test all images
    if args.auto_detect:
        print("Auto-detecting images in Custom Vision test directory...")
        image_files = find_images_in_directory()
        
        if not image_files:
            print("No image files found in current directory.")
            return
        
        print(f"Found {len(image_files)} image(s):")
        for i, img_path in enumerate(image_files, 1):
            print(f"{i}. {os.path.basename(img_path)}")
        
        print(f"\nTesting all images with threshold: {args.threshold}")
        print(f"Using high resolution upscaling: {args.upscale}x")
        print("=" * 60)
        
        for i, image_path in enumerate(image_files, 1):
            print(f"\n[{i}/{len(image_files)}] Testing: {os.path.basename(image_path)}")
            
            # Create individual folder for each image
            image_name = os.path.splitext(os.path.basename(image_path))[0]
            image_output_dir = os.path.join(output_dir, image_name)
            if not os.path.exists(image_output_dir):
                os.makedirs(image_output_dir)
            
            predictions = detector.detect_objects_from_file(image_path)
            
            if predictions:
                # Save annotated image in the image-specific folder
                output_path = os.path.join(image_output_dir, f"annotated_{image_name}.jpg")
                detector.print_detection_summary(predictions, args.threshold)
                detector.visualize_detections(image_path, predictions, output_path, args.threshold, args.upscale, not args.no_enhance)
                
                # Save detection results as JSON
                json_output_path = os.path.join(image_output_dir, f"detections_{image_name}.json")
                with open(json_output_path, 'w') as f:
                    json.dump(predictions, f, indent=2)
                print(f"Detection results saved to: {json_output_path}")
            else:
                print("No predictions returned.")
        
        print(f"\nAll images processed! Check the output files for results.")
        return
    
    # Test with image file
    if args.image:
        if not os.path.exists(args.image):
            print(f"Image file not found: {args.image}")
            return
        
        print(f"Testing object detection on: {args.image}")
        predictions = detector.detect_objects_from_file(args.image)
        
        if predictions:
            # Create image-specific subfolder in output directory
            image_name = os.path.splitext(os.path.basename(args.image))[0]
            image_output_dir = os.path.join(output_dir, image_name)
            if not os.path.exists(image_output_dir):
                os.makedirs(image_output_dir)
                print(f"Created image-specific folder: {image_output_dir}")
            
            # Save annotated image in the image-specific folder
            output_path = os.path.join(image_output_dir, f"annotated_{image_name}.jpg")
            detector.print_detection_summary(predictions, args.threshold)
            detector.visualize_detections(args.image, predictions, output_path, args.threshold, args.upscale, not args.no_enhance)
    
    # Test with image URL
    elif args.url:
        print(f"Testing object detection on URL: {args.url}")
        predictions = detector.detect_objects_from_url(args.url)
        
        if predictions:
            detector.print_detection_summary(predictions, args.threshold)
            # For URL images, we'll just print the summary since we don't have a local file to annotate
            print("\nNote: Visualization not available for URL images without downloading.")
    
    # Interactive mode
    else:
        print("Custom Vision Hexagon Detection Tester")
        print("=" * 40)
        
        while True:
            print("\nOptions:")
            print("1. Test with image file")
            print("2. Test with image URL")
            print("3. Auto-detect and test all images in current directory")
            print("4. Exit")
            
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == '1':
                # Show available images in Custom Vision test directory
                image_files = find_images_in_directory()
                if image_files:
                    print("\nAvailable images in Custom Vision test directory:")
                    for i, img_path in enumerate(image_files, 1):
                        print(f"{i}. {os.path.basename(img_path)}")
                    
                    try:
                        img_choice = input(f"\nSelect image (1-{len(image_files)}) or enter full path: ").strip()
                        
                        # Check if user selected from list
                        if img_choice.isdigit() and 1 <= int(img_choice) <= len(image_files):
                            image_path = image_files[int(img_choice) - 1]
                        else:
                            # User entered a path
                            image_path = img_choice
                        
                        if os.path.exists(image_path):
                            predictions = detector.detect_objects_from_file(image_path)
                            if predictions:
                                output_path = os.path.join(output_dir, f"single_test_{os.path.splitext(os.path.basename(image_path))[0]}.jpg")
                                detector.print_detection_summary(predictions, args.threshold)
                                detector.visualize_detections(image_path, predictions, output_path, args.threshold, args.upscale, not args.no_enhance)
                        else:
                            print(f"File not found: {image_path}")
                    except (ValueError, IndexError):
                        print("Invalid selection.")
                else:
                    image_path = input("Enter image file path: ").strip()
                    if os.path.exists(image_path):
                        predictions = detector.detect_objects_from_file(image_path)
                        if predictions:
                            detector.print_detection_summary(predictions, args.threshold)
                            detector.visualize_detections(image_path, predictions, args.output, args.threshold)
                    else:
                        print(f"File not found: {image_path}")
            
            elif choice == '2':
                image_url = input("Enter image URL: ").strip()
                predictions = detector.detect_objects_from_url(image_url)
                if predictions:
                    detector.print_detection_summary(predictions, args.threshold)
            
            elif choice == '3':
                print("Auto-detecting images in Custom Vision test directory...")
                image_files = find_images_in_directory()
                
                if not image_files:
                    print("No image files found in Custom Vision test directory.")
                    continue
                
                print(f"Found {len(image_files)} image(s):")
                for i, img_path in enumerate(image_files, 1):
                    print(f"{i}. {os.path.basename(img_path)}")
                
                confirm = input(f"\nTest all {len(image_files)} images? (y/n): ").strip().lower()
                if confirm == 'y':
                    print(f"\nTesting all images with threshold: {args.threshold}")
                    print("=" * 60)
                    
                    for i, image_path in enumerate(image_files, 1):
                        print(f"\n[{i}/{len(image_files)}] Testing: {os.path.basename(image_path)}")
                        predictions = detector.detect_objects_from_file(image_path)
                        
                        if predictions:
                            output_path = os.path.join(output_dir, f"output_{i}_{os.path.splitext(os.path.basename(image_path))[0]}.jpg")
                            detector.print_detection_summary(predictions, args.threshold)
                            detector.visualize_detections(image_path, predictions, output_path, args.threshold, args.upscale, not args.no_enhance)
                        else:
                            print("No predictions returned.")
                    
                    print(f"\nAll images processed! Check the output files for results.")
            
            elif choice == '4':
                print("Goodbye!")
                break
            
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
