from flask import Flask, request, render_template, send_from_directory
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(directory='downloads', path=filename, as_attachment=True)

@app.route('/run', methods=['POST'])
def run_scraper():
    file = request.files['html_file']
    filename = file.filename
    slug = filename.rsplit('.', 1)[0]
    os.makedirs("uploads", exist_ok=True)
    upload_path = f'uploads/{filename}'
    file.save(upload_path)

    try:
        output = subprocess.check_output(['python', 'scraper.py', upload_path], stderr=subprocess.STDOUT, text=True)

        file_links = [
            f'<a href="/download/{slug}.html"><button class="btn">HTML</button></a>',
            f'<a href="/download/menu_config_{slug}.csv"><button class="btn">Menu Config</button></a>',
            f'<a href="/download/options_config_{slug}.csv"><button class="btn">Options Config</button></a>',
            f'<a href="/download/options_{slug}.csv"><button class="btn">Options</button></a>',
            f'<a href="/download/menu_{slug}.csv"><button class="btn">Menu</button></a>',
            f'<a href="/download/images_{slug}.zip"><button class="btn">Images ZIP</button></a>',
        ]
        buttons_html = "<div class='buttons'>" + "".join(file_links) + "</div>"

        return f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: sans-serif;
                    background-color: #f9f9f9;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }}
                .container {{
                    text-align: center;
                    padding: 30px;
                    background: #fff;
                    border: 1px solid #ddd;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.05);
                }}
                .btn {{
                    background-color: #007BFF;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    margin: 5px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 16px;
                }}
                .btn:hover {{
                    background-color: #0056b3;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Scraping complete</h2>
                {buttons_html}
            </div>
        </body>
        </html>
        """

    except subprocess.CalledProcessError as e:
        return f"<pre>Error:\n{e.output}</pre>"

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
