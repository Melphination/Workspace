#!/usr/bin/env python3
"""
Python File Bundler

A script to bundle multiple Python files into a single file.
Handles imports, removes duplicates, and maintains proper structure.
"""

import ast
from pathlib import Path
from typing import List, Set, Dict, Tuple

cus_modules = "analyze combine connect_db inputs main match_utils matcher_ui matcher secure sensor share summary".split(" ")

class PythonBundler:
    def __init__(self):
        self.processed_files: Set[str] = set()
        self.imports: Set[str] = set()
        self.from_imports: Dict[str, Set[str]] = {}
        self.bundled_content: List[str] = []
        self.import_names: Set[str] = set() # obfuscate.py
        
    def extract_imports(self, tree: ast.AST) -> Tuple[List[ast.stmt], List[ast.stmt]]:
        """Extract import statements from AST and return (imports, other_statements)"""
        imports = []
        other_statements = []
        
        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in cus_modules:
                        continue
                    if alias.asname: # import ... as ...를 제대로 처리하도록 수정
                        self.imports.add(f"import {alias.name} as {alias.asname}")
                        self.import_names.add(alias.asname)
                    else:
                        self.imports.add(f"import {alias.name}")
                        self.import_names.add(alias.name)
                imports.append(node)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module in cus_modules:
                    continue
                if module not in self.from_imports:
                    self.from_imports[module] = set()
                for alias in node.names:
                    self.from_imports[module].add(alias.name)
                    self.import_names.add(alias.name)
                imports.append(node)
            else:
                other_statements.append(node)
                
        return imports, other_statements
    
    def is_local_import(self, module_name: str, base_dir: Path) -> bool:
        """Check if an import refers to a local Python file"""
        if not module_name:
            return False
            
        # Convert module notation to file path
        file_path = base_dir / f"{module_name.replace('.', '/')}.py"
        init_file = base_dir / module_name.replace('.', '/') / "__init__.py"
        
        return file_path.exists() or init_file.exists()
    
    def process_file(self, file_path: Path, base_dir: Path) -> str:
        """Process a single Python file and return its content without imports"""
        if str(file_path) in self.processed_files:
            return ""
            
        self.processed_files.add(str(file_path))
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse the AST
            tree = ast.parse(content)
            imports, other_statements = self.extract_imports(tree)
            
            # Process local imports recursively
            for imp in imports:
                if isinstance(imp, ast.ImportFrom) and imp.module:
                    if self.is_local_import(imp.module, base_dir):
                        local_file = base_dir / f"{imp.module.replace('.', '/')}.py"
                        if local_file.exists():
                            self.process_file(local_file, base_dir)
                elif isinstance(imp, ast.Import):
                    for alias in imp.names:
                        if self.is_local_import(alias.name, base_dir):
                            local_file = base_dir / f"{alias.name.replace('.', '/')}.py"
                            if local_file.exists():
                                self.process_file(local_file, base_dir)
            
            # Convert non-import statements back to source code
            if other_statements:
                # Create a new module with only non-import statements
                new_tree = ast.Module(body=other_statements, type_ignores=[])
                
                # Convert back to source code
                processed_content = ast.unparse(new_tree)
                
                return f"\n# Content from {file_path.name}\n{processed_content}\n"
            
            return ""
            
        except Exception as e:
            print(f"Warning: Could not process {file_path}: {e}")
            return f"\n# Error processing {file_path.name}: {e}\n"
    
    def generate_import_section(self) -> str:
        """Generate the consolidated import section"""
        import_lines = []
        
        # Add regular imports
        for imp in sorted(self.imports):
            import_lines.append(imp)
        
        # Add from imports
        for module, names in sorted(self.from_imports.items()):
            if names:
                names_str = ", ".join(sorted(names))
                if module:
                    import_lines.append(f"from {module} import {names_str}")
                else:
                    import_lines.append(f"from . import {names_str}")
        
        return "\n".join(import_lines) + "\n\n" if import_lines else ""
    
    def bundle_files(self, file_paths: List[Path], output_path: Path, base_dir: Path = None):
        """Bundle multiple Python files into one"""
        if base_dir is None:
            base_dir = Path.cwd()
            
        # Process all files
        for file_path in file_paths:
            if file_path.exists() and file_path.suffix == '.py':
                content = self.process_file(file_path, base_dir)
                if content.strip():
                    self.bundled_content.append(content)
            else:
                print(f"Warning: {file_path} does not exist or is not a Python file")
        
        # Generate final bundled content
        final_content = []
        
        # Add header comment
        final_content.append("#!/usr/bin/env python3")
        final_content.append('"""')
        final_content.append("Bundled Python file generated by Python File Bundler")
        final_content.append(f"Source files: {', '.join([f.name for f in file_paths])}")
        final_content.append('"""')
        final_content.append("")
        
        # Add consolidated imports
        import_section = self.generate_import_section()
        if import_section:
            final_content.append(import_section)
        
        # Add all processed content
        final_content.extend(self.bundled_content)
        
        # Write to output file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(final_content))
        
        print(f"Successfully bundled {len(file_paths)} files into {output_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Bundle multiple Python files into one')
    parser.add_argument('files', nargs='+', help='Python files to bundle')
    parser.add_argument('-o', '--output', required=True, help='Output file path')
    parser.add_argument('-b', '--base-dir', help='Base directory for resolving local imports')

    args = parser.parse_args()
        
    # Convert file paths
    file_paths = [Path(f) for f in args.files]
    output_path = Path(args.output)
    base_dir = Path(args.base_dir) if args.base_dir else Path.cwd()
        
    # Create bundler and process files
    bundler = PythonBundler()
    bundler.bundle_files(file_paths, output_path, base_dir)
