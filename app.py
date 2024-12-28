from flask import Flask, request, render_template
from bs4 import BeautifulSoup
from difflib import unified_diff
import requests
import re

app = Flask(__name__)

def extract_visible_text(html_content):
    """
    Extract visible text from HTML content, ignoring scripts, styles, and inline CSS.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove script, style, and link elements
    for element in soup(['script', 'style', 'link']):
        element.extract()

    # Remove inline styles and other attributes
    for tag in soup.find_all(True):  # Find all tags
        tag.attrs = {key: value for key, value in tag.attrs.items() if key not in ('style',)}

    # Get visible text
    text = soup.get_text()

    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def get_diff_html(text1, text2):
    """
    Generate HTML showing differences between two pieces of text.
    Additions are in green, removals are in red.
    """
    diff = unified_diff(text1.splitlines(), text2.splitlines(), lineterm='')
    diff_html = ""

    for line in diff:
        if line.startswith('+') and not line.startswith('+++'):
            diff_html += f'<span style="color: green;">{line[1:]}</span><br>'
        elif line.startswith('-') and not line.startswith('---'):
            diff_html += f'<span style="color: red;">{line[1:]}</span><br>'
        elif not line.startswith('+') and not line.startswith('-'):
            diff_html += f'{line}<br>'

    return diff_html

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compare', methods=['POST'])
def compare():
    url1 = request.form['url1']
    url2 = request.form['url2']

    try:
        # Fetch content from URLs
        html1 = requests.get(url1).text
        html2 = requests.get(url2).text

        # Extract visible text
        visible_text1 = extract_visible_text(html1)
        visible_text2 = extract_visible_text(html2)

        # Get differences as HTML
        diff_html = get_diff_html(visible_text1, visible_text2)

        if not diff_html.strip():
            # No differences found
            diff_html = '<p style="color: blue;">The HTML content is identical.</p>'

        return render_template('result.html', diff_html=diff_html)

    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':
    app.run(debug=True, port=5050)