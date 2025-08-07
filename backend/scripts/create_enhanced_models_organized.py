#!/usr/bin/env python3
"""
Updated script for organized model structure.

This script works with the organized folder structure:
- models/product/product.py
- models/product/image.py
- models/product/variant.py
- etc.
"""

import os
import sys
from pathlib import Path

def create_organized_model_structure():
    """Create the organized model folder structure."""
    
    # Create directory structure
    models_dir = Path("backend/app/models")
    product_dir = models_dir / "product"
    
    # Ensure directories exist
    product_dir.mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py files
    (models_dir / "__init__.py").touch(exist_ok=True)
    (product_dir / "__init__.py").touch(exist_ok=True)
    
    print(f"✅ Created directory structure: {product_dir}")
    
    return product_dir

def update_product_init_file():
    """Create/update the product package __init__.py file."""
    
    product_init_path = Path("backend/app/models/product/__init__.py")
    
    # Content for the __init__.py file to expose all models
    init_content = '''"""
Product Models Package

Contains all product-related models in an organized structure.
"""

from .product import Product
from .variant import ProductVariant
from .image import ProductImage
from .technical_specification import TechnicalSpecification
from .technical_drawing import TechnicalDrawing
from .size_chart import SizeChart

__all__ = [
    "Product",
    "ProductVariant", 
    "ProductImage",
    "TechnicalSpecification",
    "TechnicalDrawing",
    "SizeChart"
]
'''
    
    with open(product_init_path, 'w') as f:
        f.write(init_content)
    
    print(f"✅ Updated {product_init_path}")

def update_main_imports_organized():
    """Update main.py to import all models from the organized structure."""
    
    main_path = "backend/app/main.py"
    
    if not os.path.exists(main_path):
        print(f"❌ {main_path} not found!")
        return False
    
    with open(main_path, 'r') as f:
        content = f.read()
    
    # Updated imports for organized structure
    new_imports = '''# Import models to register them with SQLAlchemy
from .models.collection import Collection
from .models.product import (
    Product,
    ProductVariant,
    ProductImage,
    TechnicalSpecification,
    TechnicalDrawing,
    SizeChart
)'''
    
    # Replace the commented imports or existing imports
    patterns_to_replace = [
        '''# Import models to register them with SQLAlchemy (when they are created)
# from .models.user import User
# from .models.collection import Collection
# from .models.product import Product
# from .models.file import File''',
        '''# Import models to register them with SQLAlchemy
from .models.collection import Collection
from .models.product import Product
from .models.product_variant import ProductVariant
from .models.product_image import ProductImage
from .models.technical_specification import TechnicalSpecification
from .models.technical_drawing import TechnicalDrawing
from .models.size_chart import SizeChart'''
    ]
    
    # Try to replace existing imports
    replaced = False
    for pattern in patterns_to_replace:
        if pattern in content:
            content = content.replace(pattern, new_imports)
            replaced = True
            break
    
    if not replaced:
        # If no pattern matched, try to find and replace any model imports
        import re
        # Look for existing model imports and replace them
        pattern = r'# Import models.*?(?=\n\n|\n@|\napp =)'
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, new_imports, content, flags=re.DOTALL)
            replaced = True
    
    if replaced:
        with open(main_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Updated {main_path} imports for organized structure")
    else:
        print(f"⚠️  Could not find import section in {main_path} to update")
        print("📝 Please manually add these imports to main.py:")
        print(new_imports)
    
    return True

def update_existing_model_imports():
    """Update imports in existing models to work with organized structure."""
    
    # Files that might need import updates
    model_files = [
        "backend/app/models/collection.py",
        "backend/app/models/product/product.py",
        "backend/app/models/product/variant.py",
        "backend/app/models/product/image.py",
        "backend/app/models/product/technical_specification.py",
        "backend/app/models/product/technical_drawing.py",
        "backend/app/models/product/size_chart.py"
    ]
    
    updates_made = []
    
    for file_path in model_files:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            original_content = content
            
            # Update TYPE_CHECKING imports for organized structure
            if "product/product.py" in file_path:
                # Main product model imports
                old_imports = '''if TYPE_CHECKING:
    from app.models.collection import Collection
    from app.models.file import File'''
                
                new_imports = '''if TYPE_CHECKING:
    from app.models.collection import Collection
    from .variant import ProductVariant
    from .image import ProductImage
    from .technical_specification import TechnicalSpecification
    from .technical_drawing import TechnicalDrawing
    from .size_chart import SizeChart'''
                
                if old_imports in content:
                    content = content.replace(old_imports, new_imports)
                
            elif "product/" in file_path and file_path != "backend/app/models/product/product.py":
                # Other product models should import from the same package
                content = content.replace(
                    'from app.models.product import Product',
                    'from .product import Product'
                )
                content = content.replace(
                    'from app.models.product_variant import ProductVariant', 
                    'from .variant import ProductVariant'
                )
                content = content.replace(
                    'from app.models.product_image import ProductImage',
                    'from .image import ProductImage'
                )
            
            # Update collection.py imports if it references product models
            elif "collection.py" in file_path:
                content = content.replace(
                    'from app.models.product import Product',
                    'from app.models.product import Product'
                )
            
            # Write back if changes were made
            if content != original_content:
                with open(file_path, 'w') as f:
                    f.write(content)
                updates_made.append(file_path)
    
    if updates_made:
        print(f"✅ Updated imports in {len(updates_made)} files:")
        for file_path in updates_made:
            print(f"   - {file_path}")
    else:
        print("ℹ️  No import updates needed in existing model files")

def create_repository_structure():
    """Create organized repository structure to match models."""
    
    repo_dir = Path("backend/app/repositories")
    product_repo_dir = repo_dir / "product"
    
    # Create directories
    repo_dir.mkdir(parents=True, exist_ok=True)
    product_repo_dir.mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py files
    (repo_dir / "__init__.py").touch(exist_ok=True)
    (product_repo_dir / "__init__.py").touch(exist_ok=True)
    
    # Create base repository if it doesn't exist
    base_repo_path = repo_dir / "base.py"
    if not base_repo_path.exists():
        base_repo_path.write_text('''"""Base Repository - see artifact 'base_repository'"""
# Copy the BaseRepository code from the artifact here
pass
''')
        print(f"✅ Created placeholder {base_repo_path}")
    
    # Create product repository placeholder
    product_repo_path = product_repo_dir / "repository.py"
    if not product_repo_path.exists():
        product_repo_path.write_text('''"""Product Repository - see artifact 'product_repository'"""
# Copy the ProductRepository code from the artifact here
# Update imports to use: from app.models.product import Product, ProductVariant, etc.
pass
''')
        print(f"✅ Created placeholder {product_repo_path}")
    
    # Create repository __init__.py to expose classes
    product_repo_init = product_repo_dir / "__init__.py"
    product_repo_init.write_text('''"""Product Repositories Package"""

from .repository import ProductRepository

__all__ = ["ProductRepository"]
''')
    
    print(f"✅ Created repository structure: {product_repo_dir}")

def create_service_structure():
    """Create organized service structure to match models."""
    
    service_dir = Path("backend/app/services")
    product_service_dir = service_dir / "product"
    
    # Create directories
    service_dir.mkdir(parents=True, exist_ok=True)
    product_service_dir.mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py files
    (service_dir / "__init__.py").touch(exist_ok=True)
    (product_service_dir / "__init__.py").touch(exist_ok=True)
    
    # Create base service if it doesn't exist
    base_service_path = service_dir / "base.py"
    if not base_service_path.exists():
        base_service_path.write_text('''"""Base Service - see artifact 'base_service'"""
# Copy the BaseService code from the artifact here
pass
''')
        print(f"✅ Created placeholder {base_service_path}")
    
    # Create product service placeholder
    product_service_path = product_service_dir / "service.py"
    if not product_service_path.exists():
        product_service_path.write_text('''"""Product Service - see artifact 'product_service'"""
# Copy the ProductService code from the artifact here
# Update imports to use: from app.models.product import Product
# Update imports to use: from app.repositories.product import ProductRepository
pass
''')
        print(f"✅ Created placeholder {product_service_path}")
    
    # Create service __init__.py to expose classes
    product_service_init = product_service_dir / "__init__.py"
    product_service_init.write_text('''"""Product Services Package"""

from .service import ProductService

__all__ = ["ProductService"]
''')
    
    print(f"✅ Created service structure: {product_service_dir}")

def create_migration_commands():
    """Create the Alembic migration commands for organized structure."""
    
    migration_commands = '''
# Migration Commands for Organized Model Structure

## After setting up all model files:

cd backend

# 1. Create migration for new organized models
alembic revision --autogenerate -m "Add organized product models: images, specifications, technical drawings, size charts"

# 2. Apply the migration
alembic upgrade head

# 3. Test that models are properly imported
python -c "
from app.models.product import Product, ProductVariant, ProductImage
from app.models.product import TechnicalSpecification, TechnicalDrawing, SizeChart
print('✅ All organized models imported successfully!')
print(f'Product model: {Product.__name__}')
print(f'Variant model: {ProductVariant.__name__}')
print(f'Image model: {ProductImage.__name__}')
"

# 4. Create some test data (optional)
python -c "
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.product import Product, SizeChart

async def test_models():
    async with AsyncSessionLocal() as db:
        print('Database connection successful!')
        
asyncio.run(test_models())
"

## Directory Structure Created:
```
backend/app/
├── models/
│   ├── __init__.py
│   ├── collection.py
│   └── product/
│       ├── __init__.py
│       ├── product.py
│       ├── variant.py
│       ├── image.py
│       ├── technical_specification.py
│       ├── technical_drawing.py
│       └── size_chart.py
├── repositories/
│   ├── __init__.py
│   ├── base.py
│   └── product/
│       ├── __init__.py
│       └── repository.py
└── services/
    ├── __init__.py
    ├── base.py
    └── product/
        ├── __init__.py
        └── service.py
```

## Import Examples:
```python
# In your API routes or other files:
from app.models.product import Product, ProductVariant, ProductImage
from app.repositories.product import ProductRepository  
from app.services.product import ProductService
```
'''
    
    with open("backend/MIGRATION_COMMANDS_ORGANIZED.md", 'w') as f:
        f.write(migration_commands.strip())
    
    print("✅ Created backend/MIGRATION_COMMANDS_ORGANIZED.md")

def main():
    """Main function to create organized model structure."""
    
    print("🏗️  Creating Organized Virtual Showroom Models")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("backend"):
        print("❌ Error: Run this script from the project root directory")
        sys.exit(1)
    
    # Check if organized structure already exists
    product_dir = Path("backend/app/models/product")
    if not product_dir.exists():
        print("❌ Error: Product model directory not found!")
        print(f"   Expected: {product_dir}")
        print("   Please create the organized model structure first")
        sys.exit(1)
    
    # Step 1: Create organized structure if needed
    print("\n📁 Setting up organized model structure...")
    create_organized_model_structure()
    
    # Step 2: Update product package __init__.py
    print("\n📦 Updating product package __init__.py...")
    update_product_init_file()
    
    # Step 3: Update main.py imports
    print("\n📥 Updating main.py imports...")
    update_main_imports_organized()
    
    # Step 4: Update existing model imports
    print("\n🔄 Updating model imports...")
    update_existing_model_imports()
    
    # Step 5: Create repository structure
    print("\n🗄️  Creating repository structure...")
    create_repository_structure()
    
    # Step 6: Create service structure  
    print("\n🧠 Creating service structure...")
    create_service_structure()
    
    # Step 7: Create migration commands
    print("\n📋 Creating migration commands...")
    create_migration_commands()
    
    print("\n🎉 Organized Structure Setup Complete!")
    print("-" * 40)
    print("\n📋 Next Steps:")
    print("1. Copy the actual model code from artifacts into your organized files")
    print("2. Copy repository and service code from artifacts into placeholder files")
    print("3. Update any remaining import statements")
    print("4. Run migration commands from MIGRATION_COMMANDS_ORGANIZED.md")
    
    print("\n✅ Created organized structure with:")
    print("   - Product models in models/product/")
    print("   - Product repository in repositories/product/")
    print("   - Product service in services/product/")
    print("   - Updated import structure")

if __name__ == "__main__":
    main()