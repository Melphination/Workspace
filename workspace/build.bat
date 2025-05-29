python "utils/bundle.py" -o merged.py connect_db.py analyze.py combine.py inputs.py match_utils.py matcher.py matcher_ui.py secure.py sensor.py share.py summary.py main.py
python "utils/obfuscate.py" -i merged.py -o "utils/merged.py"
xcopy "C:\Users\khaji\OneDrive\Background\서울과고\정보\workspace\utils\merged.py" "C:\Users\khaji\OneDrive\build\merged.py"
xcopy "C:\Users\khaji\OneDrive\Background\서울과고\정보\workspace\sounds" "C:\Users\khaji\OneDrive\build\sounds"
xcopy "C:\Users\khaji\OneDrive\Background\서울과고\정보\workspace\images" "C:\Users\khaji\OneDrive\build\images"
xcopy "C:\Users\khaji\OneDrive\Background\서울과고\정보\workspace\.env" "C:\Users\khaji\OneDrive\build\.env"
cd "C:\Users\khaji\OneDrive\build"
nuitka --onefile merged.py --enable-plugin=tk-inter --include-data-dir=./images=images --include-data-dir=./sounds=sounds --include-data-file=./.env=.env