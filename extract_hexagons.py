import os
import json
import requests
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import argparse
from typing import List, Dict, Any

class HexagonExtractor:
    """
    Extract hexagons with high confidence (green bounding boxes) from images
    """
    
    def __init__(self, prediction_key: str, prediction_endpoint: str, project_id: str, model_name: str = "DCNE_lowres"):
        """
        Initialize the Hexagon Extractor
        
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
        
        # Construct the prediction URL
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
    
    def extract_hexagons(self, image_path: str, output_dir: str, confidence_threshold: float = 0.70):
        """
        Extract hexagons with high confidence (green bounding boxes) from an image
        
        Args:
            image_path: Path to the input image
            output_dir: Directory to save extracted hexagons
            confidence_threshold: Minimum confidence for extraction (default: 0.70 for green boxes)
        """
        try:
            # Get image name without extension for folder naming
            image_name = os.path.splitext(os.path.basename(image_path))[0]
            
            # Create subfolder for this image
            image_output_dir = os.path.join(output_dir, image_name)
            if not os.path.exists(image_output_dir):
                os.makedirs(image_output_dir)
                print(f"Created subfolder: {image_output_dir}")
            
            # Detect objects in the image
            print(f"Detecting hexagons in: {os.path.basename(image_path)}")
            predictions = self.detect_objects_from_file(image_path)
            
            if not predictions or 'predictions' not in predictions:
                print("No predictions found.")
                return
            
            # Open the image
            image = Image.open(image_path)
            img_width, img_height = image.size
            
            # Filter predictions for high confidence (green boxes)
            high_confidence_predictions = [
                pred for pred in predictions['predictions'] 
                if pred['probability'] >= confidence_threshold
            ]
            
            print(f"Found {len(high_confidence_predictions)} hexagons with confidence >= {confidence_threshold:.0%}")
            
            extracted_count = 0
            
            # Process each high-confidence prediction
            for i, prediction in enumerate(high_confidence_predictions):
                tag_name = prediction['tagName']
                probability = prediction['probability']
                bbox = prediction['boundingBox']
                
                # Convert relative coordinates to absolute pixels
                left = int(bbox['left'] * img_width)
                top = int(bbox['top'] * img_height)
                width = int(bbox['width'] * img_width)
                height = int(bbox['height'] * img_height)
                
                # Add some padding around the hexagon (10% of the box size)
                padding_x = int(width * 0.1)
                padding_y = int(height * 0.1)
                
                # Calculate crop coordinates with padding
                crop_left = max(0, left - padding_x)
                crop_top = max(0, top - padding_y)
                crop_right = min(img_width, left + width + padding_x)
                crop_bottom = min(img_height, top + height + padding_y)
                
                # Crop the hexagon from the image
                hexagon_crop = image.crop((crop_left, crop_top, crop_right, crop_bottom))
                
                # Create filename for the extracted hexagon
                hexagon_filename = f"hexagon_{i+1:03d}_conf_{probability:.0%}.png"
                hexagon_path = os.path.join(image_output_dir, hexagon_filename)
                
                # Save the extracted hexagon
                hexagon_crop.save(hexagon_path, 'PNG')
                extracted_count += 1
                
                print(f"  Extracted: {hexagon_filename} (confidence: {probability:.2%})")
            
            print(f"Successfully extracted {extracted_count} hexagons to: {image_output_dir}")
            
        except Exception as e:
            print(f"Error extracting hexagons: {str(e)}")
    
    def batch_extract_hexagons(self, input_dir: str, output_dir: str, confidence_threshold: float = 0.70):
        """
        Extract hexagons from all images in a directory
        
        Args:
            input_dir: Directory containing input images
            output_dir: Directory to save extracted hexagons
            confidence_threshold: Minimum confidence for extraction
        """
        # Create main output directory
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created main output directory: {output_dir}")
        
        # Supported image formats
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        
        # Find all images
        image_files = []
        for filename in os.listdir(input_dir):
            if any(filename.lower().endswith(ext) for ext in image_extensions):
                image_files.append(os.path.join(input_dir, filename))
        
        print(f"Found {len(image_files)} images to process")
        
        for i, image_path in enumerate(image_files, 1):
            print(f"\n{'='*60}")
            print(f"Processing image {i}/{len(image_files)}: {os.path.basename(image_path)}")
            print(f"{'='*60}")
            
            try:
                self.extract_hexagons(image_path, output_dir, confidence_threshold)
            except Exception as e:
                print(f"Error processing {image_path}: {str(e)}")
        
        print(f"\nBatch extraction complete! All hexagons saved in: {output_dir}")

def load_config(config_file: str = "config.json") -> Dict[str, str]:
    """
    Load configuration from a JSON file
    """
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Configuration file '{config_file}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error parsing configuration file '{config_file}'.")
        return None

def main():
    """
    Main function to run hexagon extraction
    """
    parser = argparse.ArgumentParser(description='Extract hexagons with high confidence from images')
    parser.add_argument('input', help='Input image file or directory')
    parser.add_argument('--output', '-o', default='extracted_hexagons', help='Output directory for extracted hexagons')
    parser.add_argument('--config', '-c', default='config.json', help='Configuration file path')
    parser.add_argument('--threshold', '-t', type=float, default=0.70, help='Confidence threshold for extraction (default: 0.70)')
    parser.add_argument('--batch', action='store_true', help='Process all images in input directory')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    if not config:
        return
    
    # Initialize the extractor
    extractor = HexagonExtractor(
        prediction_key=config['prediction_key'],
        prediction_endpoint=config['prediction_endpoint'],
        project_id=config['project_id'],
        model_name=config.get('model_name', 'DCNE_lowres')
    )
    
    if args.batch:
        # Batch processing
        if not os.path.isdir(args.input):
            print(f"Error: {args.input} is not a directory")
            return
        
        extractor.batch_extract_hexagons(args.input, args.output, args.threshold)
    
    else:
        # Single file processing
        if not os.path.isfile(args.input):
            print(f"Error: {args.input} is not a file")
            return
        
        extractor.extract_hexagons(args.input, args.output, args.threshold)

if __name__ == "__main__":
    main() 