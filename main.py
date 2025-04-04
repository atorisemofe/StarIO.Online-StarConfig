from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("STAR_API_KEY")

API_BASE_URL = "https://api.stario.online/v1/a/{groupPath}/d/{appId}/configuration"

@app.route('/', methods=['GET', 'POST'])
def index():
    alert_message = None

    if request.method == 'POST':
        app_id = request.form['appId']
        group_path = request.form['groupPath']
        cloudprnt_url = request.form['cloudprntUrl']
        printer_model = request.form['printerModel']

        api_url = API_BASE_URL.format(groupPath=group_path, appId=app_id)

        headers = {
            "Content-Type": "application/vnd.star.starconfiguration",
            "Star-Api-Key": API_KEY
        }

        payload = {
            "title": "star_configuration",
            "version": "1.5.0",
            "notification": "all",
            "print_when_completed_type": "ascii",
            "print_when_completed": "Polling Update Complete",
            "configurations": [
                {
                    "device_name": printer_model,
                    "password_protected_settings": {
                        "current_password": "public",
                        "cloudprnt": {
                            "service": "enabled",
                            "server_url": cloudprnt_url
                        }
                    }
                }
            ]
        }

        try:
            response = requests.post(api_url, json=payload, headers=headers)

            if response.status_code == 201:
                alert_message = {"success": "✅ Configuration sent successfully!"}
            else:
                # If response is not JSON, fallback to .text
                try:
                    json_response = response.json()
                    alert_message = {"error": json_response}
                except requests.exceptions.JSONDecodeError:
                    alert_message = {"error": f"{response.status_code} - {response.text.strip()}"}
        except requests.exceptions.RequestException as e:
            alert_message = {"error": str(e)}

        return render_template('index.html', alert_message=alert_message)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
