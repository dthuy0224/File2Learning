"""
Script to create backend.zip for Google Colab upload
Run this in the project root directory
"""

import zipfile
import os
from pathlib import Path

def create_backend_zip():
    """Create a zip file of the backend directory"""
    
    print("=" * 70)
    print("📦 CREATING BACKEND.ZIP FOR GOOGLE COLAB")
    print("=" * 70)
    
    backend_dir = Path("backend")
    zip_filename = "backend.zip"
    
    if not backend_dir.exists():
        print("❌ Error: 'backend' directory not found!")
        print("   Make sure you're running this from the project root")
        return
    
    # Files to exclude
    exclude_patterns = [
        '__pycache__',
        '*.pyc',
        '.pytest_cache',
        'venv',
        'uploads',
        '.git',
        '*.log',
        '.env',
        'models/difficulty_classifier/*.pt',  # Don't include old models
    ]
    
    print(f"\n📂 Creating zip from: {backend_dir.absolute()}")
    print(f"💾 Output file: {zip_filename}\n")
    
    total_files = 0
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(backend_dir):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if d not in ['__pycache__', 'venv', '.git', 'uploads']]
            
            for file in files:
                # Skip excluded files
                if any(pattern in file for pattern in ['*.pyc', '*.log', '.env']):
                    continue
                
                file_path = Path(root) / file
                arcname = file_path.relative_to(backend_dir.parent)
                
                zipf.write(file_path, arcname)
                total_files += 1
                
                if total_files % 50 == 0:
                    print(f"   Adding files... ({total_files} files)")
    
    # Get file size
    zip_size = Path(zip_filename).stat().st_size / 1024 / 1024  # MB
    
    print(f"\n✅ Zip file created successfully!")
    print(f"📊 Statistics:")
    print(f"   - Total files: {total_files}")
    print(f"   - File size: {zip_size:.2f} MB")
    print(f"   - Location: {Path(zip_filename).absolute()}")
    
    print("\n" + "=" * 70)
    print("🚀 NEXT STEPS:")
    print("=" * 70)
    print("1. Upload this file to Google Colab (Cell 11)")
    print("2. Continue with training process")
    print("=" * 70)

if __name__ == "__main__":
    try:
        create_backend_zip()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease make sure you're running this from the project root directory")

