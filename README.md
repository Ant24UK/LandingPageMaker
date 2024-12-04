
# Rendered Webpage Scraper with Embedded Resources

This Python script renders a webpage, downloads its external resources (images, stylesheets, scripts), embeds them as base64, and removes analytic scripts. The result is a self-contained HTML file that can be viewed offline with all resources included.

---

## Features

- **Fully Renders Pages**: Uses Selenium and Firefox WebDriver to fetch the dynamically rendered HTML of a webpage.
- **Embeds External Resources**: Converts images, stylesheets, and scripts into base64 data URIs and embeds them directly into the HTML.
- **Removes Analytics Scripts**: Strips out common analytics scripts for privacy and cleaner results.
- **Supports Background Images**: Processes CSS to embed background images as base64.
- **Headless Browser**: Operates without a visible browser window for efficiency.

---

## How It Works

1. **Input**: The script takes a target URL as input.
2. **Web Rendering**:
   - Uses Selenium with Firefox in headless mode to load the webpage.
   - Extracts the rendered HTML source.
3. **Resource Processing**:
   - Identifies external resources (e.g., `<img>`, `<link rel="stylesheet">`, `<script>`).
   - Downloads and encodes these resources into base64.
   - Updates the HTML to include base64 data URIs instead of external links.
4. **Output**:
   - Saves the processed HTML as `embedded_page.html`.

---

## Dependencies

To run the script, the following Python packages are required:

- `argparse`: Parses command-line arguments.
- `base64`: Encodes downloaded resources.
- `requests`: Fetches external resources.
- `urllib.parse`: Constructs and resolves URLs.
- `os`: Interacts with the filesystem.
- `tqdm`: Displays progress bars for resource downloads.
- `python-magic`: Detects MIME types.
- `selenium`: Automates web rendering.
- `webdriver-manager`: Manages the Firefox WebDriver.
- `bs4` (BeautifulSoup): Parses and modifies HTML.
- `re`: Handles regular expressions.
- `shutil`: Assists with system-level operations.

Install dependencies using `pip`:

```bash
pip install requests tqdm python-magic selenium webdriver-manager beautifulsoup4
```

You also need [GeckoDriver](https://github.com/mozilla/geckodriver), but the script can install it automatically using `webdriver-manager`.

---

## Usage

Run the script from the command line with the following arguments:

```bash
python LPM.py -t <TARGET_URL> [-v]
```

### Arguments

- `-t, --target-url` (required): The URL of the webpage to scrape.
- `-v, --verbose` (optional): Enables verbose output for detailed processing logs.

### Example

```bash
python LPM.py -t "https://example.com" -v
```
![image](https://github.com/user-attachments/assets/1a1d18f8-cb9a-4eab-8d3e-fb4679b9de62)

---

## Output

The script generates a file named `embedded_page.html` in the current directory. This file is a self-contained version of the target webpage, suitable for offline viewing.

---

## Known Limitations

- **Large Pages**: Pages with many resources can result in a large output file and slow processing.
- **JavaScript-Heavy Sites**: Some JavaScript-driven dynamic content may not render fully.
- **Unsupported Resource Types**: Non-standard MIME types may not embed correctly.

---

## License

This project is released under the MIT License. Feel free to use and modify it as needed.
