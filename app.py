import mistune
import frontmatter
import os
from flask import Flask, render_template, abort

app = Flask(__name__)

# Get the base directory of your project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index():
    posts_dir = "content/posts"
    posts = []

    # Loop through folders in content/posts
    for folder in os.listdir(posts_dir):
        folder_path = os.path.join(posts_dir, folder)
        if os.path.isdir(folder_path):
            # Load the index.md to get the title
            post_file = os.path.join(folder_path, "index.md")
            if os.path.exists(post_file):
                post = frontmatter.load(post_file)
                posts.append({
                    'slug': folder,
                    'title': post.get('title', folder),
                    'date': post.get('date', 'No Date')
                })

    return render_template('index.html', posts=posts)

@app.route('/posts/<name>')
def show_post(name):
    posts_root = os.path.realpath(os.path.join(BASE_DIR, "content", "posts"))
    path = os.path.realpath(os.path.join(posts_root, name, "index.md"))

    # Prevent path traversal: resolved path must stay within posts_root
    if os.path.commonpath([posts_root, path]) != posts_root:
        abort(404)

    if not os.path.exists(path):
        abort(404)

	# 1. Load the file using frontmatter
    post = frontmatter.load(path)

    # 2. Extract metadata (title, date, tags, etc.)
    # .get() is safer in case 'title' is missing in the md file
    post_title = post.get('title', 'Untitled Post')
    post_date = post.get('date', '...')

    # 3. Convert only the Markdown body to HTML
    content_html = mistune.html(post.content)

    # 4. Pass both to the template
    return render_template('post.html', date=post_date, title=post_title, content=content_html)

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "false").strip().lower() in ("1", "true", "yes", "on")
    app.run(debug=debug_mode)
