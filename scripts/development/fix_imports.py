#!/usr/bin/env python3
"""
Script to convert all absolute imports to relative imports in afiliadohub/api
"""

import os
import re

def fix_imports_in_file(filepath):
    """Convert absolute imports to relative imports in a single file"""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Patterns to replace (handlers, utils, models, services)
    replacements = [
        (r'from api\.handlers\.', 'from .handlers.'),  # In index.py
        (r'from api\.utils\.', 'from ..utils.'),       # In handlers/
        (r'from api\.models\.', 'from ..models.'),     # In handlers/
        (r'from api\.services\.', 'from ..services.'), # In handlers/
    ]
    
    # Determine location to adjust patterns
    if '/handlers/' in filepath.replace('\\', '/'):
        # In handlers directory, use .. for utils/models
        pass
    elif '/utils/' in filepath.replace('\\', '/'):
        # In utils directory
        replacements = [
            (r'from api\.utils\.', 'from .'),
            (r'from api\.handlers\.', 'from ..handlers.'),
        ]
    elif 'index.py' in filepath:
        # In index.py, use . for same-level imports
        replacements = [
            (r'from api\.handlers\.', 'from .handlers.'),
            (r'from api\.utils\.', 'from .utils.'),
            (r'from api\.models\.', 'from .models.'),
            (r'from api\.services\.', 'from .services.'),
        ]
    
    # Apply replacements
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # Only write if changed
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fixed: {filepath}")
        return True
    return False

def main():
    """Fix all Python files in afiliadohub/api"""
    api_dir = r'c:\ProjetoAfiliadoTop\afiliadohub\api'
    
    fixed_count = 0
    
    for root, dirs, files in os.walk(api_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if fix_imports_in_file(filepath):
                    fixed_count += 1
    
    print(f"\n🎉 Fixed {fixed_count} files")

if __name__ == '__main__':
    main()
