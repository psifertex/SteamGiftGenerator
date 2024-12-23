import requests
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from io import BytesIO
from PIL import Image
import argparse
import csv
import os
from tempfile import NamedTemporaryFile
import html

def fetch_steam_game_details(app_id):
    url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
    response = requests.get(url)
    data = response.json()
    
    if str(app_id) in data and data[str(app_id)]['success']:
        game_data = data[str(app_id)]['data']
        return {
            'name': html.unescape(game_data.get('name', 'Unknown Game')),
            'image_url': game_data.get('header_image', ''),
            'description': html.unescape(game_data.get('short_description', 'No description available.')),
            'genres': html.unescape(", ".join([genre['description'] for genre in game_data.get('genres', [])])),
            'categories': html.unescape(", ".join([category['description'] for category in game_data.get('categories', [])]))
        }
    return None

def search_steam_game(query):
    url = "https://store.steampowered.com/search/suggest"
    params = {
        'term': query,
        'f': 'games',
        'cc': 'US'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.text
        start_index = data.find("/app/") + 5
        end_index = data.find("/", start_index)
        if start_index > 4 and end_index > start_index:
            return data[start_index:end_index]
    return None

def wrap_text(text, max_width, c):
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        if c.stringWidth(current_line + " " + word, "Helvetica", 10) <= max_width:
            current_line += (" " if current_line else "") + word
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

def generate_gift_card_page(c, gift_code, details, x_offset, y_offset, width, height):
    margin = 20
    game_name = details['name']
    image_url = details['image_url']
    description = details['description']
    genres = details['genres']
    categories = details['categories']

    # Add game name
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(x_offset + width / 2, y_offset + height - margin, f"Game: {game_name}")

    # Add gift code
    c.setFont("Courier-Bold", 12)
    c.drawCentredString(x_offset + width / 2, y_offset + height - margin - 20, f"Gift Code: {gift_code}")

    # Add description
    c.setFont("Helvetica", 8)
    description_lines = wrap_text(description, width - 2 * margin, c)
    for i, line in enumerate(description_lines):
        c.drawString(x_offset + margin, y_offset + height - margin - 40 - (i * 10), line)

    # Add genres
    genres_lines = wrap_text(f"Genres: {genres}", width - 2 * margin, c)
    for i, line in enumerate(genres_lines):
        c.drawString(x_offset + margin, y_offset + height - margin - 55 - (len(description_lines) * 10) - (i * 10), line)

    # Add categories
    categories_lines = wrap_text(f"Categories: {categories}", width - 2 * margin, c)
    for i, line in enumerate(categories_lines):
        c.drawString(x_offset + margin, y_offset + height - margin - 70 - (len(description_lines) * 10) - (len(genres_lines) * 10) - (i * 10), line)

    # Download and add game image
    if image_url:
        image_data = requests.get(image_url).content
        with NamedTemporaryFile(delete=False, suffix=".png") as temp_image:
            temp_image.write(image_data)
            temp_image_path = temp_image.name

        image = Image.open(temp_image_path)
        image_width, image_height = image.size
        aspect_ratio = image_height / image_width
        img_width = width - 2 * margin
        img_height = img_width * aspect_ratio
        if img_height > height - margin - 105 - (len(description_lines) * 10):
            img_height = height - margin - 105 - (len(description_lines) * 10)
            img_width = img_height / aspect_ratio

        img_x = x_offset + (width - img_width) / 2
        img_y = y_offset + (height - img_height - margin - 105 - (len(description_lines) * 10))
        c.drawImage(temp_image_path, img_x, img_y, img_width, img_height)
        os.remove(temp_image_path)

def generate_gift_cards_from_csv(csv_file, output_file):
    with open(csv_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        c = canvas.Canvas(output_file, pagesize=landscape(letter))
        width, height = landscape(letter)
        margin = 20
        card_width = (width - 3 * margin) / 2
        card_height = (height - 3 * margin) / 2
        for i, row in enumerate(reader):
            if i % 4 == 0 and i != 0:
                c.showPage()
            gift_code = row['Key']
            game_input = row['ID_or_Name']
            x_offset = margin + (i % 2) * (card_width + margin)
            y_offset = height - margin - ((i % 4) // 2 + 1) * (card_height + margin)
            try:
                app_id = int(game_input)
            except ValueError:
                app_id = search_steam_game(game_input)

            details = fetch_steam_game_details(app_id) if app_id else None
            if details:
                generate_gift_card_page(c, gift_code, details, x_offset, y_offset, card_width, card_height)
        c.save()
        print(f"PDF saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Steam gift cards as PDFs.")
    parser.add_argument("--csv", type=str, required=True, help="Path to a CSV file containing Keys and IDs or Names.")
    parser.add_argument("--output", type=str, default="steam_gift_cards.pdf", help="Output PDF file name.")
    args = parser.parse_args()
    generate_gift_cards_from_csv(args.csv, args.output)
