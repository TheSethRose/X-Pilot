from app import create_app
from flask import render_template
import os
import jinja2
from pathlib import Path

app = create_app()

with app.app_context():
    print("Template folder:", app.template_folder)
    print("Jinja loader type:", type(app.jinja_loader))

    # Safely join path
    if app.template_folder:
        template_path = os.path.join(app.template_folder, "main/index.html")
        print(f"Full template path: {template_path}")
        print(f"Template exists: {os.path.exists(template_path)}")

        try:
            print("Trying to load template directly from file...")
            with open(template_path, 'r') as f:
                print(f"First 100 chars of template: {f.read(100)}")
        except Exception as e:
            print(f"Error reading template file: {e}")
    else:
        print("Template folder is None")

    try:
        result = render_template("main/index.html")
        print("Template rendered successfully")
    except Exception as e:
        print(f"Error rendering template: {e}")

    # Try with a simple direct jinja2 environment
    try:
        if app.template_folder:
            template_loader = jinja2.FileSystemLoader(app.template_folder)
            template_env = jinja2.Environment(loader=template_loader)
            template = template_env.get_template("main/index.html")
            print("Template loaded with direct Jinja2 Environment")
        else:
            print("Cannot create Jinja2 environment with None template_folder")
    except Exception as e:
        print(f"Error loading template with Jinja2: {e}")
