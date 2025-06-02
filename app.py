from flask import Flask, request, render_template, send_from_directory
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(directory='downloads', path=filename, as_attachment=True)

@app.route('/run', methods=['POST'])
def run_scraper():
    url = request.form['url']
    try:
        output = subprocess.check_output(['python', 'scraper.py', url], stderr=subprocess.STDOUT, text=True)

        # Extract slug from URL
        slug = url.strip('/').split('/')[-1]

        file_links = [
            f'<a href="/download/{slug}.html"><button>HTML</button></a>',
            f'<a href="/download/menu_config_{slug}.csv"><button>Menu Config</button></a>',
            f'<a href="/download/options_config_{slug}.csv"><button>Options Config</button></a>',
            f'<a href="/download/options_{slug}.csv"><button>Options</button></a>',
            f'<a href="/download/menu_{slug}.csv"><button>Menu</button></a>',
            f'<a href="/download/images_{slug}.zip"><button>Images ZIP</button></a>',
        ]
        buttons_html = "<br>".join(file_links)
        return f"<p>✅ Scraping complete.</p>{buttons_html}"

    except subprocess.CalledProcessError as e:
        return f"<pre>Error:\n{e.output}</pre>"


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
