import os
import json
import requests
import argparse
from typing import List, Dict, Any
from PIL import Image
import base64
import io
import sys

# Fix encoding issues on Windows
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

class HexagonInfoExtractor:
    """
    Extract information from hexagon images using GPT-4 Vision API
    """
    
    def __init__(self, api_key: str, endpoint: str):
        """
        Initialize the Hexagon Info Extractor
        
        Args:
            api_key: OpenAI API key
            endpoint: GPT-4 Vision API endpoint
        """
        self.api_key = api_key
        self.endpoint = endpoint
        
        # Headers for the API request
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """
        Encode image to base64 string
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded image string
        """
        try:
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
            
            # Encode to base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            return base64_image
            
        except Exception as e:
            print(f"Error encoding image: {str(e)}")
            return None
    
    def extract_info_from_hexagon(self, image_path: str) -> Dict[str, Any]:
        """
        Extract information from a single hexagon image using GPT-4 Vision
        
        Args:
            image_path: Path to the hexagon image
            
        Returns:
            Dictionary containing extracted information
        """
        try:
            # Encode the image
            base64_image = self.encode_image_to_base64(image_path)
            if not base64_image:
                return None
            
            # Prepare the prompt for GPT-4 Vision
            prompt = """
            First, analyze this image and determine if it contains a hexagon shape.
            
            If the image contains a hexagon:
            1. Extract the text information inside the hexagon in the following format:
               - Upper line: [text/value on the upper part of the hexagon]
               - Lower line: [text/value on the lower part of the hexagon]
            
            2. If there's only one line of text, put it in the upper line and leave lower line empty.
            3. If there are more than two lines, combine them appropriately.
            
            4. Focus on extracting:
               - Numbers, letters, symbols
               - Unit measurements (if any)
               - Any technical specifications
               - Room numbers, equipment codes, etc.
            
            5. Return the information in this exact JSON format:
            {
                "is_hexagon": true,
                "upper_line": "text here",
                "lower_line": "text here"
            }
            
            If the image does NOT contain a hexagon:
            Return this JSON format:
            {
                "is_hexagon": false,
                "upper_line": "",
                "lower_line": "",
                "reason": "brief explanation of what was found instead"
            }
            
            Be precise and include all visible text within the hexagon boundaries if a hexagon is present.
            """
            
            # Prepare the request payload for OpenAI API
            payload = {
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.1
            }
            
            # Make the API request
            print(f"Analyzing: {os.path.basename(image_path)}")
            response = requests.post(
                self.endpoint,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            # Check if the request was successful
            response.raise_for_status()
            
            # Parse the response
            result = response.json()
            
            # Extract the content from the response
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                
                # Try to parse JSON from the response
                try:
                    # Look for JSON in the response
                    start_idx = content.find('{')
                    end_idx = content.rfind('}') + 1
                    
                    if start_idx != -1 and end_idx != 0:
                        json_str = content[start_idx:end_idx]
                        extracted_info = json.loads(json_str)
                        
                        # Add the image filename for reference
                        extracted_info['image_file'] = os.path.basename(image_path)
                        extracted_info['confidence'] = self.extract_confidence_from_filename(image_path)
                        
                        return extracted_info
                    else:
                        # If no JSON found, create a structured response
                        return {
                            "image_file": os.path.basename(image_path),
                            "confidence": self.extract_confidence_from_filename(image_path),
                            "upper_line": content.strip(),
                            "lower_line": "",
                            "raw_response": content
                        }
                        
                except json.JSONDecodeError:
                    # If JSON parsing fails, return the raw response
                    return {
                        "image_file": os.path.basename(image_path),
                        "confidence": self.extract_confidence_from_filename(image_path),
                        "upper_line": content.strip(),
                        "lower_line": "",
                        "raw_response": content
                    }
            else:
                print(f"No response content found for {image_path}")
                return None
                
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error for {image_path}: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None
        except Exception as e:
            print(f"Error extracting info from {image_path}: {str(e)}")
            return None
    
    def extract_confidence_from_filename(self, image_path: str) -> str:
        """
        Extract confidence level from the image filename
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Confidence level as string
        """
        filename = os.path.basename(image_path)
        if 'conf_' in filename:
            # Extract confidence from filename like "hexagon_001_conf_100%.png"
            try:
                conf_part = filename.split('conf_')[1].split('.')[0]
                return conf_part
            except:
                return "unknown"
        return "unknown"
    
    def process_hexagon_folder(self, hexagon_folder: str, output_file: str):
        """
        Process all hexagon images in a folder and save results to a file
        
        Args:
            hexagon_folder: Path to folder containing hexagon images
            output_file: Path to save the extracted information
        """
        try:
            # Get all PNG files in the folder
            hexagon_files = []
            for filename in os.listdir(hexagon_folder):
                if filename.lower().endswith('.png'):
                    hexagon_files.append(os.path.join(hexagon_folder, filename))
            
            if not hexagon_files:
                print(f"No PNG files found in {hexagon_folder}")
                return
            
            # Sort files by hexagon number
            hexagon_files.sort()
            
            print(f"Found {len(hexagon_files)} hexagon images to process")
            print(f"Processing folder: {os.path.basename(hexagon_folder)}")
            print("=" * 60)
            
            # Process each hexagon image
            results = []
            for i, hexagon_path in enumerate(hexagon_files, 1):
                print(f"\n[{i}/{len(hexagon_files)}] Processing: {os.path.basename(hexagon_path)}")
                
                extracted_info = self.extract_info_from_hexagon(hexagon_path)
                
                if extracted_info:
                    results.append(extracted_info)
                    
                    # Check if it's actually a hexagon
                    is_hexagon = extracted_info.get('is_hexagon', True)
                    
                    if is_hexagon:
                        upper = extracted_info.get('upper_line', '')
                        lower = extracted_info.get('lower_line', '')
                        print(f"  [OK] Hexagon detected: Upper='{upper}' Lower='{lower}'")
                    else:
                        reason = extracted_info.get('reason', 'No hexagon found')
                        print(f"  [WARN] Not a hexagon: {reason}")
                else:
                    print(f"  [ERROR] Failed to extract information")
                
                # Add a small delay to avoid rate limiting
                import time
                time.sleep(1)
            
            # Save results to file
            if results:
                # Save all results (including false positives)
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                
                # Create a new file with only true hexagons
                true_hexagons = [result for result in results if result.get('is_hexagon', False)]
                true_hexagons_file = output_file.replace('.json', '_true_hexagons.json')
                
                with open(true_hexagons_file, 'w', encoding='utf-8') as f:
                    json.dump(true_hexagons, f, indent=2, ensure_ascii=False)
                
                print(f"\n{'='*60}")
                print(f"Extraction complete! Results saved to: {output_file}")
                print(f"True hexagons only saved to: {true_hexagons_file}")
                print(f"Successfully processed {len(results)} out of {len(hexagon_files)} hexagons")
                print(f"True hexagons found: {len(true_hexagons)}")
                print(f"False positives: {len(results) - len(true_hexagons)}")
                
                # Print summary (only true hexagons)
                print(f"\nExtracted Information Summary (True Hexagons Only):")
                print("-" * 50)
                for result in true_hexagons:
                    print(f"File: {result['image_file']}")
                    print(f"  Upper: {result.get('upper_line', 'N/A')}")
                    print(f"  Lower: {result.get('lower_line', 'N/A')}")
                    print(f"  Confidence: {result.get('confidence', 'N/A')}")
                    print()
            else:
                print("No information was extracted from any hexagon images.")
                
        except Exception as e:
            print(f"Error processing hexagon folder: {str(e)}")

def main():
    """
    Main function to run hexagon information extraction
    """
    parser = argparse.ArgumentParser(description='Extract information from hexagon images using GPT-4 Vision')
    parser.add_argument('hexagon_folder', help='Path to folder containing hexagon images')
    parser.add_argument('--output', '-o', help='Output JSON file path (default: hexagon_info.json)')
    parser.add_argument('--api-key', help='OpenAI API key (if not provided, will use default)')
    parser.add_argument('--endpoint', help='GPT-4 Vision API endpoint (if not provided, will use default)')
    
    args = parser.parse_args()
    
    # Default values
    default_api_key = "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"
    default_endpoint = "https://api.openai.com/v1/chat/completions"
    
    # Use provided values or defaults
    api_key = args.api_key if args.api_key else default_api_key
    endpoint = args.endpoint if args.endpoint else default_endpoint
    
    # Generate output filename if not provided
    if args.output:
        output_file = args.output
    else:
        folder_name = os.path.basename(args.hexagon_folder)
        output_file = f"{folder_name}_info.json"
    
    # Check if hexagon folder exists
    if not os.path.exists(args.hexagon_folder):
        print(f"Error: Hexagon folder '{args.hexagon_folder}' does not exist.")
        return
    
    # Initialize the extractor
    extractor = HexagonInfoExtractor(api_key, endpoint)
    
    # Process the hexagon folder
    extractor.process_hexagon_folder(args.hexagon_folder, output_file)

if __name__ == "__main__":
    main() 