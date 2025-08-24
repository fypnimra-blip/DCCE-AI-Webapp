# DCNE - Document Content Network Extraction

A Python-based tool for extracting and analyzing hexagon-shaped elements from technical documents and engineering drawings using Azure Custom Vision AI. Now includes a modern Streamlit web interface for easy interaction and deployment.

## Overview

DCNE (Document Content Network Extraction) is designed to automatically detect, extract, and analyze hexagon-shaped elements from technical documents, particularly useful for engineering drawings, mechanical plans, and architectural documents. The tool uses Azure Custom Vision Object Detection to identify hexagons with high confidence and provides comprehensive analysis capabilities.

## Features

- **AI-Powered Detection**: Uses Azure Custom Vision for accurate hexagon detection
- **Modern Web Interface**: Streamlit-based web application for easy interaction
- **Image Enhancement**: Multiple enhancement levels to improve detection accuracy
- **Batch Processing**: Process multiple images simultaneously
- **Confidence Filtering**: Extract only high-confidence detections
- **Visualization**: Generate annotated images with bounding boxes
- **Data Export**: Export detection results in JSON format
- **Image Preprocessing**: Line thickening and visibility enhancement
- **High-Resolution Processing**: Upscale images for better detection
- **Real-time Processing**: Live progress tracking and status updates

## Project Structure

```
DCNE/
├── DCNE.py                      # Main detection and visualization script
├── hexagon_detection_app.py     # Streamlit web application
├── extract_hexagons.py          # Hexagon extraction utility
├── enhance_visibility.py        # Image enhancement tool
├── thicken_lines.py             # Line thickening utility
├── upscale_images.py            # Image upscaling tool
├── extract_hexagon_info.py      # Hexagon information extraction
├── enhanced_hexagon_processor.py # Enhanced hexagon processing
├── config.json                  # Azure Custom Vision configuration
├── requirements.txt             # Python dependencies
├── streamlit_requirements.txt   # Streamlit-specific dependencies
├── output/                      # Generated output files
│   ├── enhanced_east_images/    # Enhanced input images
│   ├── thickened_east_images/   # Line-thickened images
│   └── *.jpg                    # Detection visualization results
├── extracted_hexagons/          # Individual extracted hexagons
│   └── [image_name]/            # Organized by source image
├── temp-directory/              # Temporary processing directories
└── *.json                       # Detection results and metadata
```

## Installation

### Prerequisites

- Python 3.7 or higher (Python 3.13.5 recommended)
- Azure Custom Vision account with trained model
- Valid Azure Custom Vision API credentials
- Streamlit (for web interface)

### Setup

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd DCNE
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Azure Custom Vision**
   
   Update `config.json` with your Azure Custom Vision credentials:
   ```json
   {
     "prediction_key": "your_prediction_key",
     "prediction_endpoint": "https://your-endpoint.cognitiveservices.azure.com/",
     "project_id": "your_project_id",
     "model_name": "your_model_name"
   }
   ```

4. **Run the Streamlit Web App**
   ```bash
   streamlit run hexagon_detection_app.py
   ```
   
   The app will be available at `http://localhost:8501`

## Usage

### Web Interface (Recommended)

The easiest way to use DCNE is through the Streamlit web interface:

```bash
streamlit run hexagon_detection_app.py
```

This provides:
- Drag-and-drop image upload
- Real-time processing progress
- Interactive results visualization
- Easy configuration management

### Command Line Interface

#### Basic Hexagon Detection

```bash
python DCNE.py --image path/to/your/image.jpg
```

#### Extract High-Confidence Hexagons

```bash
python extract_hexagons.py --input path/to/image.jpg --output extracted_hexagons/
```

#### Enhance Image Visibility

```bash
python enhance_visibility.py --input path/to/image.jpg --output enhanced_image.png --level strong
```

#### Batch Process Multiple Images

```bash
python extract_hexagons.py --input input_directory/ --output extracted_hexagons/ --confidence 0.70
```

#### Thicken Lines for Better Detection

```bash
python thicken_lines.py --input path/to/image.jpg --output thickened_image.png
```

## Configuration Options

### Confidence Thresholds
- **Green boxes**: High confidence (≥70%) - typically actual hexagons
- **Yellow boxes**: Medium confidence (50-70%) - potential hexagons
- **Red boxes**: Low confidence (<50%) - likely false positives

### Enhancement Levels
- **mild**: Subtle enhancement for already clear images
- **medium**: Balanced enhancement
- **strong**: Aggressive enhancement (default)
- **extreme**: Maximum enhancement for very poor quality images

## Output Formats

### Detection Results
The tool generates JSON files containing:
- Detection confidence scores
- Bounding box coordinates
- Hexagon classification results
- Text content within hexagons (if applicable)

### Visual Outputs
- Annotated images with colored bounding boxes
- Individual extracted hexagon images
- Enhanced and preprocessed images

## Dependencies

- `requests>=2.28.0` - HTTP requests for Azure API
- `Pillow>=9.0.0` - Image processing
- `matplotlib>=3.5.0` - Visualization and plotting
- `numpy>=1.21.0` - Numerical operations
- `streamlit>=1.28.0` - Web application framework
- `openai>=1.0.0` - OpenAI API integration (optional)

## API Configuration

To use this tool, you need:

1. **Azure Custom Vision Account**: Create an account at [Azure Custom Vision](https://www.customvision.ai/)
2. **Trained Model**: Train a custom object detection model for hexagon detection
3. **API Credentials**: Obtain prediction key, endpoint, and project ID
4. **Published Model**: Ensure your model is published and accessible

## Streamlit Web Application

The DCNE Streamlit app provides a modern, user-friendly interface for hexagon detection:

### Features
- **Drag & Drop Upload**: Easy image upload with drag-and-drop functionality
- **Real-time Processing**: Live progress tracking with step-by-step status updates
- **Interactive Results**: View detection results with annotated images
- **Configuration Management**: Easy access to Azure Custom Vision settings
- **Batch Processing**: Process multiple images through the web interface
- **Download Results**: Download processed images and JSON data

### Running the App
```bash
streamlit run hexagon_detection_app.py
```

The app will automatically open in your default browser at `http://localhost:8501`

## Example Workflow

### Using the Web Interface (Recommended)
1. **Start the App**: Run `streamlit run hexagon_detection_app.py`
2. **Upload Images**: Drag and drop your technical documents
3. **Configure Settings**: Adjust confidence thresholds and enhancement levels
4. **Process Images**: Click "Process Images" and monitor real-time progress
5. **Download Results**: Save processed images and detection data

### Using Command Line
1. **Prepare Images**: Place your technical documents in an input directory
2. **Enhance Images**: Use `enhance_visibility.py` to improve image quality
3. **Detect Hexagons**: Run `DCNE.py` for initial detection and visualization
4. **Extract Hexagons**: Use `extract_hexagons.py` to extract high-confidence detections
5. **Analyze Results**: Review JSON output files for detailed analysis

## Troubleshooting

### Common Issues

1. **API Authentication Errors**
   - Verify your `config.json` credentials
   - Ensure your Azure Custom Vision model is published
   - Check API quota and limits

2. **Low Detection Accuracy**
   - Try different enhancement levels
   - Use line thickening for technical drawings
   - Upscale images for better resolution

3. **Memory Issues**
   - Process images in smaller batches
   - Reduce image resolution if needed
   - Close other applications to free memory

### Performance Tips

- Use SSD storage for faster I/O operations
- Process images in batches for efficiency
- Adjust confidence thresholds based on your needs
- Use appropriate enhancement levels for your image quality

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the troubleshooting section
- Review Azure Custom Vision documentation
- Open an issue in the repository

## Acknowledgments

- Azure Custom Vision for AI-powered object detection
- PIL/Pillow for image processing capabilities
- Matplotlib for visualization features 