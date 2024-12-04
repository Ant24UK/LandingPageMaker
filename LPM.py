import argparse
import base64
import requests
from urllib.parse import urljoin, urlparse
import os
from tqdm import tqdm
import magic
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
import re
import shutil

# Function to get geckodriver path or install it if not found
def get_geckodriver_path(verbose=False):
    # Check if geckodriver is already in PATH
    geckodriver_path = shutil.which("geckodriver")
    
    if geckodriver_path:
        if verbose:
            print(f"GeckoDriver found at {geckodriver_path}")
        return geckodriver_path
    else:
        # If geckodriver is not found, install it using webdriver_manager
        if verbose:
            print("GeckoDriver not found. Installing...")
        geckodriver_path = GeckoDriverManager().install()
        if verbose:
            print(f"GeckoDriver installed at {geckodriver_path}")
        return geckodriver_path

# Function to download a resource and return its content as base64
def download_and_embed(url, resource_type='image', verbose=False):
    try:
        # Filter out invalid URLs (data URIs, etc.)
        if url.startswith('data:') or not urlparse(url).netloc:
            if verbose:
                print(f"Skipping invalid URL: {url[:500]}")  # Output only first 500 chars of invalid URL
            return None  # Don't print anything else for invalid URLs
        
        # Print verbose output
        if verbose:
            print(f"Downloading {url}...")

        # Send the request to download the resource
        response = requests.get(url)
        response.raise_for_status()
        
        # Get the file content
        file_content = response.content
        
        # Use python-magic to detect MIME type of the resource
        mime = magic.Magic(mime=True)
        mime_type = mime.from_buffer(file_content)
        
        # For images, we don't need to specify mime, it's auto-detected
        if resource_type == 'image':
            if mime_type.startswith('image'):
                mime_type = mime_type
            else:
                mime_type = 'application/octet-stream'
        elif resource_type == 'script':
            mime_type = 'application/javascript'
        elif resource_type == 'stylesheet':
            mime_type = 'text/css'
        
        # Encode the content in base64
        encoded_content = base64.b64encode(file_content).decode('utf-8')
        
        # Return a data URI for embedding
        return f"data:{mime_type};base64,{encoded_content}"
    
    except Exception as e:
        return None

# Function to remove analytic scripts from the HTML
def remove_analytics_scripts(soup, verbose=False):
    # List of patterns to detect analytic scripts
    analytics_patterns = [
        r"google-analytics",  # Google Analytics
        r"analytics.js",      # Google Analytics older version
        r"gtag.js",           # Google Tag Manager
        r"adobe.com",         # Adobe Analytics
        r"piwik.js",          # Piwik (now Matomo)
        r"statcounter.com",    # StatCounter
        r"mixpanel.com",       # Mixpanel
        r"segment.com",        # Segment
        # Add any other analytics service URL patterns here
    ]
    
    # Find and remove <script> tags that match these patterns
    for script_tag in soup.find_all('script', src=True):
        src_url = script_tag['src']
        if any(re.search(pattern, src_url, re.IGNORECASE) for pattern in analytics_patterns):
            if verbose:
                print(f"Removing analytics script: {src_url}")
            script_tag.decompose()  # Remove the script tag
    
    return soup

# Function to replace external resource links in HTML with base64-encoded content
def embed_resources_in_html(html, base_url, verbose=False):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove analytic scripts
    soup = remove_analytics_scripts(soup, verbose)
    
    resources = []
    
    # Replace image tags
    if verbose:
        print("Finding image tags to embed...")
    for img_tag in soup.find_all('img'):
        img_url = img_tag.get('src')
        if img_url:
            full_url = urljoin(base_url, img_url)  # Handle relative URLs
            resources.append((full_url, 'image', img_tag))
    
    # Replace script tags
    if verbose:
        print("Finding script tags to embed...")
    for script_tag in soup.find_all('script', src=True):
        script_url = script_tag['src']
        full_url = urljoin(base_url, script_url)
        resources.append((full_url, 'script', script_tag))
    
    # Replace link (stylesheet) tags
    if verbose:
        print("Finding stylesheet tags to embed...")
    for link_tag in soup.find_all('link', rel='stylesheet'):
        css_url = link_tag.get('href')
        if css_url:
            full_url = urljoin(base_url, css_url)
            resources.append((full_url, 'stylesheet', link_tag))
    
    # Process inline styles (background-image URLs)
    for style_tag in soup.find_all('style'):
        css_content = style_tag.string
        if css_content:
            updated_css = embed_background_images_in_css(css_content, base_url)
            style_tag.string = updated_css

    # Initialize tqdm progress bar
    with tqdm(total=len(resources), desc="Downloading resources", unit="resource") as pbar:
        # Iterate over the resources and embed them
        for url, resource_type, tag in resources:
            base64_content = download_and_embed(url, resource_type, verbose)
            if base64_content:
                if resource_type == 'image':
                    tag['src'] = base64_content
                elif resource_type == 'script':
                    tag['src'] = base64_content
                elif resource_type == 'stylesheet':
                    tag['href'] = base64_content
                elif resource_type == 'style':
                    updated_css = embed_background_images_in_css(tag.string, base_url, verbose)
                    tag.string = updated_css
            pbar.update(1)
    
    return str(soup)

# Function to replace background-image URLs in CSS with base64-encoded content
def embed_background_images_in_css(css, base_url):
    # Match all background-image URLs in the CSS (e.g., background-image: url('path/to/image.jpg'))
    url_pattern = re.compile(r'url\((["\']?)(.*?)\1\)')

    def replace_url(match):
        image_url = match.group(2)
        full_url = urljoin(base_url, image_url)  # Handle relative URLs
        base64_img = download_and_embed(full_url, 'image')
        if base64_img:
            return f"url({base64_img})"
        return match.group(0)

    return url_pattern.sub(replace_url, css)

# Set up argparse to accept the target URL as an argument
parser = argparse.ArgumentParser(description="Fetch rendered HTML and embed external resources.")
parser.add_argument('-t', '--target-url', required=True, help="The target URL to scrape.")
parser.add_argument('-v', '--verbose', action='store_true', help="Enable verbose output.")
args = parser.parse_args()

# Verbose output for connecting
if args.verbose:
    print(f"Connecting to {args.target_url}...")

# Get geckodriver path or install it if necessary
geckodriver_path = get_geckodriver_path(verbose=args.verbose)

# Set Firefox options for headless mode
options = Options()
options.add_argument("--headless")

# Create the Service object
service = Service(geckodriver_path)

# Set up Firefox WebDriver with headless option
if args.verbose:
    print("Launching Firefox WebDriver in headless mode...")

# Pass the Service object to the WebDriver
driver = webdriver.Firefox(service=service, options=options)

# Open the webpage
if args.verbose:
    print(f"Opening webpage {args.target_url}...")
driver.get(args.target_url)

# Get the fully rendered source code
if args.verbose:
    print("Rendering page and extracting HTML source...")
rendered_source = driver.page_source

# Close the browser
if args.verbose:
    print("Closing browser...")
driver.quit()

# Extract the base URL (in case there are relative paths in the HTML)
base_url = args.target_url

# Embed the external resources
if args.verbose:
    print("Embedding external resources into HTML...")

final_html = embed_resources_in_html(rendered_source, base_url, verbose=args.verbose)

# Output the final HTML (or save it to a file)
if args.verbose:
    print("Saving the embedded HTML to 'embedded_page.html'...")

with open('embedded_page.html', 'w', encoding='utf-8') as f:
    f.write(final_html)

print("Embedded HTML saved as 'embedded_page.html'.")
