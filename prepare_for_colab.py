"""
Helper Script: Prepare Project for Google Colab Training
Tạo file backend.zip ready để upload lên Colab

Usage:
    python prepare_for_colab.py
"""

import zipfile
import os
from pathlib import Path
from datetime import datetime

def create_backend_zip():
    """Create backend.zip for Colab upload"""
    
    print("=" * 70)
    print("📦 Preparing File2Learning for Google Colab")
    print("=" * 70)
    print()
    
    # Get project root
    project_root = Path(__file__).parent
    backend_dir = project_root / 'backend'
    
    if not backend_dir.exists():
        print("❌ Error: backend/ folder not found!")
        print(f"   Looking in: {project_root}")
        return
    
    print(f"📂 Backend directory: {backend_dir}")
    
    # Output ZIP file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_filename = f'backend_for_colab_{timestamp}.zip'
    zip_path = project_root / zip_filename
    
    print(f"📦 Creating: {zip_filename}")
    print()
    
    # Files to exclude (không cần thiết cho training)
    exclude_patterns = [
        '__pycache__',
        '*.pyc',
        '.pytest_cache',
        'venv',
        'env',
        '.env',
        '.git',
        'logs',
        'uploads',
        '*.log',
        'Dockerfile',
        'docker-compose.yml',
        'alembic.ini',
        'alembic/versions/*.py',  # Keep structure but skip migration files
    ]
    
    def should_exclude(filepath):
        """Check if file should be excluded"""
        path_str = str(filepath)
        for pattern in exclude_patterns:
            if pattern in path_str:
                return True
        return False
    
    # Create ZIP
    file_count = 0
    total_size = 0
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(backend_dir):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not should_exclude(Path(root) / d)]
            
            for file in files:
                file_path = Path(root) / file
                
                if should_exclude(file_path):
                    continue
                
                # Get relative path from backend parent
                arcname = file_path.relative_to(backend_dir.parent)
                
                try:
                    zipf.write(file_path, arcname)
                    file_size = file_path.stat().st_size
                    total_size += file_size
                    file_count += 1
                    
                    # Show progress for large files
                    if file_size > 1024 * 1024:  # > 1MB
                        print(f"  ➕ {arcname} ({file_size / 1024 / 1024:.1f} MB)")
                
                except Exception as e:
                    print(f"  ⚠️  Skipped {arcname}: {e}")
    
    # Summary
    zip_size = zip_path.stat().st_size
    
    print()
    print("=" * 70)
    print("✅ ZIP Created Successfully!")
    print("=" * 70)
    print(f"📦 File: {zip_filename}")
    print(f"📊 Size: {zip_size / 1024 / 1024:.2f} MB")
    print(f"📁 Files: {file_count}")
    print(f"💾 Original size: {total_size / 1024 / 1024:.2f} MB")
    print(f"📉 Compression: {(1 - zip_size/total_size) * 100:.1f}%")
    print()
    print("📋 Next Steps:")
    print("  1. Go to: https://colab.research.google.com")
    print("  2. Upload: backend/File2Learning_Colab_Training.ipynb")
    print("  3. Enable GPU (Runtime → Change runtime type → GPU)")
    print(f"  4. Upload this file: {zip_filename}")
    print("  5. Run all cells and wait ~10 minutes")
    print()
    print("📖 For detailed guide, see: backend/COLAB_QUICKSTART.md")
    print("=" * 70)


if __name__ == '__main__':
    create_backend_zip()

