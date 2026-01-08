#!/bin/bash
set -e

# Create output directory
rm -rf _site
mkdir _site

# Copy static files
# We use individual cp commands or a loop to avoid errors if files are missing,
# although we expect them to be there.
files=("index.html" "stylesheet.css" "favicon.ico" "robots.txt" "sitemap.xml" ".nojekyll" "CNAME")

for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    cp "$file" _site/
  else
    echo "Warning: $file not found"
  fi
done

# Copy root images (JPGs and PNGs)
# Use find or shell expansion carefully
cp *.JPG _site/ 2>/dev/null || true
cp *.png _site/ 2>/dev/null || true

# Copy images directory
if [ -d "images" ]; then
  cp -r images _site/
fi

echo "Build complete in _site/"
