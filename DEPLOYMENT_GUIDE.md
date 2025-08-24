# 🚀 Hexagon Detection App - Deployment Guide

## 📁 File Storage Options

### **Current Development Setup**
- **Temporary Files**: `./temp-directory/` (project folder)
- **Output Files**: `./output/` (project folder)
- **Issue**: User-specific paths, won't work for other users

### **Production Deployment Options**

#### **Option 1: Local Server Storage (Recommended for Small Scale)**
```bash
# Set environment variables
export DEPLOYMENT_MODE=production
export STORAGE_TYPE=local

# Files will be stored in:
# - Temp: /tmp/hexagon_detection/ (Linux) or C:\Users\AppData\Local\Temp\hexagon_detection\ (Windows)
# - Output: /tmp/hexagon_output/ (Linux) or C:\Users\AppData\Local\Temp\hexagon_output\ (Windows)
```

#### **Option 2: Shared Network Storage (Recommended for Enterprise)**
```bash
# Set environment variables
export DEPLOYMENT_MODE=production
export STORAGE_TYPE=shared

# Files will be stored in:
# - Temp: /shared/uploads/hexagon_detection/
# - Output: /shared/results/hexagon_output/
```

#### **Option 3: Cloud Storage (Recommended for Scalability)**
```python
# Add to requirements.txt
boto3==1.26.0  # For AWS S3
azure-storage-blob==12.17.0  # For Azure Blob
google-cloud-storage==2.8.0  # For Google Cloud Storage
```

## 🛠️ Deployment Steps

### **Step 1: Choose Storage Type**
```bash
# For local server deployment
export DEPLOYMENT_MODE=production
export STORAGE_TYPE=local

# For shared network deployment
export DEPLOYMENT_MODE=production
export STORAGE_TYPE=shared

# For cloud deployment
export DEPLOYMENT_MODE=production
export STORAGE_TYPE=cloud
```

### **Step 2: Set Up File Permissions**
```bash
# Create shared directories (if using shared storage)
sudo mkdir -p /shared/uploads/hexagon_detection
sudo mkdir -p /shared/results/hexagon_output
sudo chmod 755 /shared/uploads /shared/results
sudo chown www-data:www-data /shared/uploads /shared/results
```

### **Step 3: Deploy the App**
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run hexagon_detection_app.py --server.port 8501
```

### **Step 4: Set Up Auto-Cleanup**
```bash
# Add to crontab for automatic cleanup (Linux)
0 2 * * * /usr/bin/python3 /path/to/your/app/cleanup_old_files.py

# Or create a Windows scheduled task
```

## 🔧 Cloud Storage Integration

### **AWS S3 Example**
```python
import boto3
from deployment_config import config

class S3Storage:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.bucket_name = 'your-hexagon-app-bucket'
    
    def upload_file(self, file_path: str, s3_key: str):
        self.s3.upload_file(file_path, self.bucket_name, s3_key)
    
    def download_file(self, s3_key: str, local_path: str):
        self.s3.download_file(self.bucket_name, s3_key, local_path)
```

### **Azure Blob Storage Example**
```python
from azure.storage.blob import BlobServiceClient
from deployment_config import config

class AzureStorage:
    def __init__(self):
        self.connection_string = "your_connection_string"
        self.container_name = "hexagon-app-container"
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
```

## 📊 Storage Requirements

### **Per User Session**
- **Uploaded Image**: ~2-10 MB
- **Extracted Hexagons**: ~1-5 MB (37 hexagon images)
- **JSON Files**: ~10-50 KB
- **Final Mapped Image**: ~2-10 MB
- **Total per session**: ~5-25 MB

### **Server Storage Recommendations**
- **Small Scale** (< 100 users/day): 10 GB
- **Medium Scale** (100-1000 users/day): 100 GB
- **Large Scale** (> 1000 users/day): 1 TB + Cloud Storage

## 🔒 Security Considerations

### **File Access Control**
```python
# Set proper file permissions
os.chmod(file_path, 0o644)  # Read/write for owner, read for others
```

### **Temporary File Cleanup**
```python
# Clean up files after processing
import shutil
shutil.rmtree(temp_directory)
```

### **User Session Isolation**
```python
# Each user gets unique session ID
session_id = str(uuid.uuid4())
temp_dir = config.get_temp_directory(session_id)
```

## 🚀 Deployment Platforms

### **Streamlit Cloud**
```toml
# .streamlit/config.toml
[server]
port = 8501
enableCORS = false
enableXsrfProtection = false

[theme]
primaryColor = "#1f77b4"
```

### **Docker Deployment**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "hexagon_detection_app.py", "--server.port=8501"]
```

### **Kubernetes Deployment**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hexagon-detection-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: hexagon-detection
  template:
    metadata:
      labels:
        app: hexagon-detection
    spec:
      containers:
      - name: hexagon-app
        image: your-registry/hexagon-detection:latest
        ports:
        - containerPort: 8501
        env:
        - name: DEPLOYMENT_MODE
          value: "production"
        - name: STORAGE_TYPE
          value: "cloud"
```

## 📝 Environment Variables

| Variable | Description | Default | Options |
|----------|-------------|---------|---------|
| `DEPLOYMENT_MODE` | Deployment environment | `development` | `development`, `production` |
| `STORAGE_TYPE` | Storage backend | `local` | `local`, `shared`, `cloud` |
| `AWS_ACCESS_KEY_ID` | AWS S3 access key | - | Your AWS key |
| `AWS_SECRET_ACCESS_KEY` | AWS S3 secret key | - | Your AWS secret |
| `AZURE_STORAGE_CONNECTION_STRING` | Azure connection string | - | Your Azure connection string |

## 🔄 Migration from Development to Production

1. **Update file paths** in the app
2. **Set environment variables** for production
3. **Configure storage backend**
4. **Set up monitoring and logging**
5. **Test with multiple users**
6. **Deploy to production server**

## 📞 Support

For deployment issues:
1. Check environment variables
2. Verify file permissions
3. Test storage connectivity
4. Review server logs
5. Contact system administrator
