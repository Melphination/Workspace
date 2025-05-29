import argparse, os, subprocess
from bundle import PythonBundler
from obfuscate import obfuscate
from pathlib import Path

parser = argparse.ArgumentParser()

parser.add_argument("-i", "--input", nargs="+", required=True, type=str)
parser.add_argument("-o", "--output", required=True, type=str)
parser.add_argument("-fo", "--add-folder", nargs="*", required=False, type=str)
parser.add_argument("-fi", "--add-file", nargs="*", required=False, type=str)
parser.add_argument('-p', '--plugin', nargs='*', required=False, type=str)

args = parser.parse_args()
# Convert file paths
input_paths = [Path(f) for f in args.input]
output_path = Path(args.output)
code_path = os.path.join(output_path, "release.py")
folder_path = [Path(f) for f in args.add_folder]
file_path = [Path(f) for f in args.add_file]
base_dir = Path.cwd()

os.makedirs(output_path, exist_ok=True)

# Create bundler and process files
bundler = PythonBundler()
bundler.bundle_files(input_paths, code_path, base_dir)

with open(code_path, "r", encoding="utf-8") as f:
    code = f.read()

obfuscated_code = obfuscate(code, bundler.import_names)

with open(code_path, "w", encoding="utf-8") as f:
    f.write(obfuscated_code)

plugins = ["--enable-plugin=" + p for p in args.plugins] if args.plugins else []
folders = [f"--include-data-dir={f}={f}" for f in folder_path]
files = [f"--include-data-file={f}={f}" for f in file_path]

subprocess.run(["nuitka", "--onefile", code_path, *plugins,  *folders, *files])
