from flask import Flask, request, Response, jsonify
import requests

app = Flask(__name__)

# Initialize request counter
request_counter = 0

@app.route('/')
def home():
    # HTML content with favicon and dynamic title (without the <img> tag)
    html_content = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>requests handled: {request_counter}</title>
        <!-- Link to favicon -->
        <link rel="icon" href="/static/logo.png" type="image/png">
    </head>
    <body>
        <div style="text-align: center; margin-top: 50px;">
            <h1>Server is running</h1>
            <p>Total requests handled: {request_counter}</p>
        </div>
    </body>
    </html>
    '''
    return Response(html_content, content_type='text/html')

@app.route('/bot<bot_token>/<path:telegram_method>', methods=['POST', 'GET'])
def proxy_to_telegram(bot_token, telegram_method):
    global request_counter
    request_counter += 1  # Increment the request counter

    # Full URL to the Telegram server
    telegram_url = f"https://api.telegram.org/bot{bot_token}/{telegram_method}"

    try:
        # Forward request to Telegram
        if request.method == 'POST':
            if 'multipart/form-data' in request.content_type:
                # Handle file uploads
                files = {key: (file.filename, file) for key, file in request.files.items()}
                data = request.form.to_dict()  # Other request parameters
                response = requests.post(telegram_url, data=data, files=files)
            else:
                # Handle simple POST requests
                response = requests.post(telegram_url, json=request.json)
        else:
            # Handle GET requests
            response = requests.get(telegram_url, params=request.args)
        
        # Return Telegram's response to the requester exactly as received
        return Response(response.content, status=response.status_code, content_type=response.headers.get('Content-Type'))
    
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to forward request to Telegram: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
