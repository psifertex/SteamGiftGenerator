# Steam Gift Card Generator

This project generates Steam gift cards as PDFs using game details fetched from the Steam store.

## Features

- Fetches game details from the Steam store using the game ID or name.
- Generates a PDF with gift cards containing game details and a gift code.
- Supports batch processing from a CSV file.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/SteamGiftGenerator.git
    cd SteamGiftGenerator
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Preview

![Preview](preview.png)

## Usage

1. Prepare a CSV file with the following columns:
    - `Key`: The gift code.
    - `ID_or_Name`: The Steam game ID or name.

2. Run the script to generate the PDF:
    ```sh
    python __init__.py --csv path/to/yourfile.csv --output output.pdf
    ```

    - `--csv`: Path to the CSV file containing Keys and IDs or Names.
    - `--output`: (Optional) Output PDF file name. Default is `steam_gift_cards.pdf`.

## Example

Example CSV file (`games.csv`):
```csv
Key,ID_or_Name
XXXXX-XXXXX-XXXXX,440
XXXXX-XXXXX-XXXXX,Portal 2
XXXXX-XXXXX-XXXXX,The Witcher
```

Generate the PDF:
```sh
python __init__.py --csv games.csv --output my_gift_cards.pdf
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
