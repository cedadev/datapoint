echo 1. Converting
jupyter nbconvert --to rst ../demo/basic_usage.ipynb 

echo 2. Relocating
mv ../demo/basic_usage.rst usage.rst

echo 3. Reformatting
python rst_format.py usage.rst

echo 4. Installing
mv usage.rst source/usage.rst