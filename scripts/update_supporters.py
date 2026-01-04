import csv
import requests
from bs4 import BeautifulSoup
import io
from datetime import datetime
import re

# URL of the published Google Sheet CSV
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSxt3SXANj2NU-2UHlFRHhJLVJOdx1HBVxekMcHtkhAMzwp5E4ftBJ1DPlx7LMelBYd7d800_PmShJi/pub?gid=1418573323&single=true&output=csv"

def update_supporters():
    # 1. Fetch the CSV data
    response = requests.get(CSV_URL)
    response.raise_for_status()

    csv_content = response.content.decode('utf-8')
    csv_reader = csv.reader(io.StringIO(csv_content))

    # Skip header
    header = next(csv_reader, None)

    top_supporters = []
    supporters = []

    # 2. Parse the CSV
    for row in csv_reader:
        if not row:
            continue

        # Ensure we have at least one column (Name)
        if len(row) < 1:
            continue

        name = row[0].strip()
        if not name:
            continue

        # Check for "Top Supporter" flag safely
        is_top = False
        if len(row) >= 2:
            is_top = row[1].strip().upper() == 'TRUE'

        if is_top:
            top_supporters.append(name)
        else:
            supporters.append(name)

    # Combine lists, top supporters first
    all_supporters = top_supporters + supporters

    # 3. Update index.html
    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # Update Supporters Grid
    supporters_list = soup.find('div', id='supporters-list')
    if supporters_list:
        supporters_list.clear()
        for name in all_supporters:
            # Create a div for each supporter
            div = soup.new_tag('div')
            div.string = name
            supporters_list.append(div)

    # Update Last Updated timestamp
    last_updated_p = soup.find('p', id='last-updated')
    if last_updated_p:
        current_date = datetime.now().strftime("%B %d, %Y")
        last_updated_p.string = f"Last updated: {current_date}"

    # Update years operating
    years_operating_span = soup.find('span', id='years-operating')
    if years_operating_span:
        start_date = datetime(2020, 6, 18)
        years = (datetime.now() - start_date).days / 365.25
        years_operating_span.string = f"{int(years)} years"

    # 4. Save the file
    # specific prettier to minimize damage
    html_output = soup.prettify(formatter="html")

    # Post-process to fix inline spacing for the dynamic year count
    # Prettify often adds newlines around tags, which creates unwanted whitespace in text.
    # Matches: "For over", whitespace, <span...>, whitespace, "X years", whitespace, </span>, whitespace, ", we"
    pattern = r'For over\s*<span id="years-operating">\s*(\d+ years)\s*</span>\s*, we'
    replacement = r'For over <span id="years-operating">\1</span>, we'
    html_output = re.sub(pattern, replacement, html_output)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_output)

if __name__ == "__main__":
    update_supporters()
