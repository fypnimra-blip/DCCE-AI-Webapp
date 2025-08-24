import json
import argparse
import os
from PIL import Image, ImageDraw, ImageFont
import re
from collections import defaultdict

def extract_hexagon_number(filename):
    """
    Extract hexagon number from filename like 'hexagon_001_conf_100%.png'
    """
    match = re.search(r'hexagon_(\d+)', filename)
    if match:
        return int(match.group(1))
    return None

def count_duplicate_hexagons(true_hexagons_json_path):
    """
    Count duplicate hexagons with the same upper and lower lines
    """
    try:
        with open(true_hexagons_json_path, 'r', encoding='utf-8') as f:
            true_hexagons = json.load(f)
        
        # Create a dictionary to count duplicates
        hexagon_counts = defaultdict(list)
        
        for hexagon in true_hexagons:
            upper = hexagon.get('upper_line', '')
            lower = hexagon.get('lower_line', '')
            key = f"{upper}/{lower}"
            hexagon_counts[key].append(hexagon)
        
        # Find duplicates
        duplicates = {}
        for key, hexagons in hexagon_counts.items():
            if len(hexagons) > 1:
                duplicates[key] = {
                    'count': len(hexagons),
                    'hexagons': hexagons
                }
        
        return duplicates
        
    except Exception as e:
        print(f"Error counting duplicates: {str(e)}")
        return {}

def map_true_hexagons_to_image(original_image_path, true_hexagons_json_path, output_image_path, detection_json_path=None):
    """
    Map only true hexagons back to the original image and highlight them in green
    """
    try:
        # Load the original image
        print(f"Loading original image: {original_image_path}")
        original_image = Image.open(original_image_path)
        original_width, original_height = original_image.size
        print(f"Original image size: {original_width}x{original_height}")
        
        # Load the true hexagons JSON
        print(f"Loading true hexagons data: {true_hexagons_json_path}")
        with open(true_hexagons_json_path, 'r', encoding='utf-8') as f:
            true_hexagons = json.load(f)
        
        print(f"Found {len(true_hexagons)} true hexagons to map")
        
        # Count all instances (including unique ones)
        hexagon_counts = defaultdict(list)
        
        for hexagon in true_hexagons:
            upper = hexagon.get('upper_line', '')
            lower = hexagon.get('lower_line', '')
            key = f"{upper}/{lower}"
            hexagon_counts[key].append(hexagon)
        
        # Create all_instances dictionary (including unique ones)
        all_instances = {}
        duplicates = {}
        
        for key, hexagons in hexagon_counts.items():
            count = len(hexagons)
            all_instances[key] = {
                'count': count,
                'hexagons': hexagons
            }
            # Also store duplicates separately
            if count > 1:
                duplicates[key] = {
                    'count': count,
                    'hexagons': hexagons
                }
        
        if duplicates:
            print(f"\nDuplicate Hexagons Found:")
            print("-" * 40)
            for key, info in duplicates.items():
                print(f"• {key}: {info['count']} instances")
                for hexagon in info['hexagons']:
                    print(f"  - {hexagon.get('image_file', 'Unknown')} (confidence: {hexagon.get('confidence', 'N/A')})")
        
        print(f"\nAll Instances Found:")
        print("-" * 40)
        for key, info in all_instances.items():
            print(f"• {key}: {info['count']} instance{'s' if info['count'] > 1 else ''}")
        
        # Load detection results if available
        detections = {}
        if detection_json_path and os.path.exists(detection_json_path):
            with open(detection_json_path, 'r') as f:
                detection_data = json.load(f)
                # Parse detection data into hexagon number mapping
                predictions = detection_data.get('predictions', {}).get('predictions', [])
                for i, detection in enumerate(predictions, 1):
                    detections[i] = detection.get('boundingBox', {})
        
        # Create a copy of the original image for annotation
        annotated_image = original_image.copy()
        draw = ImageDraw.Draw(annotated_image)
        
        # Try to load a font for text annotation
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            try:
                font = ImageFont.load_default()
            except:
                font = None
        
        # Process each true hexagon
        mapped_count = 0
        for hexagon_data in true_hexagons:
            image_file = hexagon_data.get('image_file', '')
            hexagon_number = extract_hexagon_number(image_file)
            
            if hexagon_number is None:
                print(f"Could not extract hexagon number from: {image_file}")
                continue
            
            # Get detection coordinates
            if hexagon_number in detections:
                bbox = detections[hexagon_number]
            else:
                # Use simplified positioning if no detection data available
                print(f"No detection data for hexagon #{hexagon_number}, using simplified positioning")
                bbox = {
                    'left': 0.1 + (hexagon_number * 0.05) % 0.8,
                    'top': 0.1 + (hexagon_number * 0.03) % 0.8,
                    'width': 0.04,
                    'height': 0.04
                }
            
            # Extract bounding box coordinates
            left = bbox.get('left', 0)
            top = bbox.get('top', 0)
            width = bbox.get('width', 0)
            height = bbox.get('height', 0)
            
            # Convert normalized coordinates to pixel coordinates
            x1 = int(left * original_width)
            y1 = int(top * original_height)
            x2 = int((left + width) * original_width)
            y2 = int((top + height) * original_height)
            
            # Draw green rectangle around the hexagon
            draw.rectangle([x1, y1, x2, y2], outline='green', width=3)
            
            # Add text annotation
            upper_text = hexagon_data.get('upper_line', '')
            lower_text = hexagon_data.get('lower_line', '')
            confidence = hexagon_data.get('confidence', 'N/A')
            
            # Create label text
            label_text = f"#{hexagon_number}"
            if upper_text or lower_text:
                label_text += f" ({upper_text}/{lower_text})"
            
            # Draw text background
            if font:
                text_bbox = draw.textbbox((x1, y1 - 20), label_text, font=font)
                draw.rectangle(text_bbox, fill='green', outline='white')
                draw.text((x1, y1 - 20), label_text, fill='white', font=font)
            else:
                # Simple text without font
                draw.text((x1, y1 - 15), label_text, fill='green')
            
            mapped_count += 1
            print(f"Mapped hexagon #{hexagon_number}: {upper_text}/{lower_text}")
        
        # Save the annotated image
        annotated_image.save(output_image_path, 'JPEG', quality=95)
        
        print(f"\nSuccessfully mapped {mapped_count} true hexagons!")
        print(f"Annotated image saved to: {output_image_path}")
        
        # Save duplicate analysis to JSON
        duplicate_analysis_path = output_image_path.replace('.jpg', '_duplicate_analysis.json')
        with open(duplicate_analysis_path, 'w', encoding='utf-8') as f:
            json.dump({
                'total_hexagons': len(true_hexagons),
                'unique_combinations': len(set(f"{h.get('upper_line', '')}/{h.get('lower_line', '')}" for h in true_hexagons)),
                'all_instances': all_instances,
                'duplicates': duplicates,
                'summary': {key: info['count'] for key, info in all_instances.items()}
            }, f, indent=2, ensure_ascii=False)
        print(f"Instance analysis saved to: {duplicate_analysis_path}")
        
        return True
        
    except Exception as e:
        print(f"Error mapping hexagons: {str(e)}")
        return False

def main():
    """
    Main function to run the enhanced hexagon mapping
    """
    parser = argparse.ArgumentParser(description='Enhanced hexagon mapping with duplicate counting')
    parser.add_argument('original_image', help='Path to the original image')
    parser.add_argument('true_hexagons_json', help='Path to the JSON file with only true hexagons')
    parser.add_argument('--output', '-o', help='Output image path (optional)')
    parser.add_argument('--detection-json', '-d', help='Path to detection results JSON (optional)')
    
    args = parser.parse_args()
    
    # Check if files exist
    if not os.path.exists(args.original_image):
        print(f"Error: Original image '{args.original_image}' does not exist.")
        return
    
    if not os.path.exists(args.true_hexagons_json):
        print(f"Error: True hexagons JSON '{args.true_hexagons_json}' does not exist.")
        return
    
    # Generate output filename if not provided
    if args.output:
        output_path = args.output
    else:
        # Create True-hexagons subfolder in the JSON folder
        json_folder = os.path.dirname(args.true_hexagons_json)
        true_hexagons_folder = os.path.join(json_folder, "True-hexagons")
        
        # Create the True-hexagons folder if it doesn't exist
        if not os.path.exists(true_hexagons_folder):
            os.makedirs(true_hexagons_folder)
            print(f"Created folder: {true_hexagons_folder}")
        
        # Get the original image name
        original_image_name = os.path.splitext(os.path.basename(args.original_image))[0]
        output_path = os.path.join(true_hexagons_folder, f"{original_image_name}_true_hexagons_mapped.jpg")
    
    # Map the hexagons
    success = map_true_hexagons_to_image(
        args.original_image, 
        args.true_hexagons_json, 
        output_path,
        args.detection_json
    )
    
    if success:
        print(f"\nEnhanced hexagon mapping completed successfully!")
    else:
        print(f"\nEnhanced hexagon mapping failed!")

if __name__ == "__main__":
    main()
