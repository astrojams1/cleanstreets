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

# Copy images directory
if [ -d "images" ]; then
  cp -r images _site/
fi

# Copy data directory
if [ -d "data" ]; then
  cp -r data _site/
fi

echo "Build complete in _site/"
