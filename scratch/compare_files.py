import os
import filecmp
from pathlib import Path

def compare_dirs(src_dir, ref_dir, ignore_dirs=None):
    if ignore_dirs is None:
        ignore_dirs = {'.git', '.venv', 'node_modules', '.next', 'scratch', '__pycache__', '.mypy_cache', '.pytest_cache', '.ruff_cache', 'dist'}
        
    src_path = Path(src_dir)
    ref_path = Path(ref_dir)
    
    only_in_ref = []
    different_files = []
    
    for ref_file_path in ref_path.rglob('*'):
        if any(part in ignore_dirs for part in ref_file_path.relative_to(ref_path).parts):
            continue
        if ref_file_path.is_dir():
            continue
            
        rel_path = ref_file_path.relative_to(ref_path)
        src_file_path = src_path / rel_path
        
        if not src_file_path.exists():
            only_in_ref.append(str(rel_path))
        else:
            if not filecmp.cmp(ref_file_path, src_file_path, shallow=False):
                different_files.append(str(rel_path))
                
    return only_in_ref, different_files

if __name__ == '__main__':
    src = r'D:\ADPilot'
    ref = r'D:\ADPilot\scratch\old_adpilot'
    
    only_in_ref, different = compare_dirs(src, ref)
    
    print("=== Files only in Remote develop branch ===")
    for f in only_in_ref:
        print(f)
        
    print("\n=== Files that differ between Local and Remote develop ===")
    for f in different:
        print(f)
