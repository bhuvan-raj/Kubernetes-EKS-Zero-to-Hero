# k8s-config-secret-lab/app.py

from flask import Flask, render_template_string
import os
import time # To potentially observe file update delays

app = Flask(__name__)

@app.route('/')
def home():
    # --- Read ConfigMap values from environment variables ---
    app_title = os.getenv('APP_TITLE', 'Default App Title')
    welcome_message = os.getenv('WELCOME_MESSAGE', 'Welcome to the default application!')
    log_level = os.getenv('APP_LOG_LEVEL', 'INFO')
    new_config_value = os.getenv('NEW_CONFIG_VALUE', 'Not Updated Yet')


    # --- Read Secret values from mounted files ---
    db_username = "NOT_LOADED"
    db_password_display = "**SECRET_NOT_LOADED**" # We'll just display a placeholder
    api_key_display = "**SECRET_NOT_LOADED**" # We'll just display a placeholder

    secret_path = "/etc/app-secrets/"
    try:
        # Read DB_USERNAME from file
        with open(os.path.join(secret_path, 'DB_USERNAME'), 'r') as f:
            db_username = f.read().strip()
        # Read DB_PASSWORD from file (and acknowledge its presence)
        with open(os.path.join(secret_path, 'DB_PASSWORD'), 'r') as f:
            _ = f.read().strip() # Read but don't store/display directly for security
            db_password_display = "**SECRET_LOADED**"
        # Read API_KEY from file (and acknowledge its presence)
        with open(os.path.join(secret_path, 'API_KEY'), 'r') as f:
            _ = f.read().strip() # Read but don't store/display directly for security
            api_key_display = "**SECRET_LOADED**"
        print(f"Successfully loaded secrets from {secret_path}")
    except FileNotFoundError as e:
        print(f"ERROR: Secret file not found: {e}. Running without secret data.")
        pass # Secrets might not be mounted in development or certain scenarios
    except Exception as e:
        print(f"An unexpected error occurred reading secrets: {e}")
        pass

    # Basic styling for the HTML output
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{app_title}</title>
        <style>
            body {{ font-family: sans-serif; margin: 2em; background-color: #f0f4f8; color: #333; line-height: 1.6; }}
            .container {{ max-width: 800px; margin: 0 auto; background-color: #ffffff; padding: 2em; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
            h1 {{ color: #2c3e50; border-bottom: 2px solid #eceff1; padding-bottom: 10px; }}
            h2 {{ color: #34495e; margin-top: 1.5em; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
            p {{ margin-bottom: 0.8em; }}
            strong {{ color: #e74c3c; }}
            em {{ color: #7f8c8d; font-size: 0.9em; }}
            .config-value {{ background-color: #ecf0f1; padding: 0.5em; border-radius: 5px; font-family: monospace; }}
            .secret-value {{ background-color: #fdeded; padding: 0.5em; border-radius: 5px; font-family: monospace; color: #c0392b; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{app_title}</h1>
            <p><strong>ConfigMap Data:</strong></p>
            <ul>
                <li><strong>Welcome Message:</strong> <span class="config-value">{welcome_message}</span></li>
                <li><strong>Application Log Level:</strong> <span class="config-value">{log_level}</span></li>
                <li><strong>New Config Value:</strong> <span class="config-value">{new_config_value}</span> <em>(Observe this for updates!)</em></li>
            </ul>

            <h2>Secret Data (Sensitized Display)</h2>
            <p>
                <em>For security, actual secret values are not displayed. We only confirm their successful loading.</em>
            </p>
            <ul>
                <li><strong>Database User:</strong> <span class="secret-value">{db_username}</span></li>
                <li><strong>Database Password:</strong> <span class="secret-value">{db_password_display}</span></li>
                <li><strong>External API Key:</strong> <span class="secret-value">{api_key_display}</span></li>
            </ul>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template)

if __name__ == '__main__':
    # Flask runs on port 5000 by default
    app.run(host='0.0.0.0', port=5000)
