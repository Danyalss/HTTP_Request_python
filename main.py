from quart import Quart, request, jsonify, Response
import aiohttp
import logging

app = Quart(__name__)

# Initialize request counter
request_counter = 0

# Setup logging configuration
logging.basicConfig(filename='requests.log', level=logging.INFO, format='%(asctime)s - %(message)s')

async def forward_request_to_telegram(telegram_url, method, data=None, files=None):
    async with aiohttp.ClientSession() as session:
        if method == 'POST':
            if files:
                # Send a POST request with files
                form_data = aiohttp.FormData()
                for key, (filename, file_content, content_type) in files.items():
                    form_data.add_field(key, file_content, filename=filename, content_type=content_type)
                async with session.post(telegram_url, data=form_data) as response:
                    return await response.text(), response.status
            else:
                # Send a simple POST request
                async with session.post(telegram_url, json=data) as response:
                    return await response.text(), response.status
        else:
            # Send a GET request
            async with session.get(telegram_url, params=data) as response:
                return await response.text(), response.status

@app.route('/')
async def home():
    global request_counter
    # HTML content with favicon and dynamic title
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
            # <img src="/static/logo.png" alt="Site Logo" style="width: 150px; height: auto;"/>
            <h1>Server is running</h1>
            <p>Total requests handled: {request_counter}</p>
        </div>
    </body>
    </html>
    '''
    return Response(html_content, content_type='text/html')

@app.route('/bot<bot_token>/<path:telegram_method>', methods=['POST', 'GET'])
async def proxy_to_telegram(bot_token, telegram_method):
    global request_counter
    request_counter += 1  # Increment the request counter

    # Log request details
    logging.info(f'Received request for bot token: {bot_token}, method: {telegram_method}, data: {await request.get_data()}')

    # Full URL to the Telegram server
    telegram_url = f"https://api.telegram.org/bot{bot_token}/{telegram_method}"

    # Forward request to Telegram
    try:
        if request.method == 'POST':
            if 'multipart/form-data' in request.content_type:  # Check if the request includes files
                files = {key: (file.filename, await file.read(), file.content_type) for key, file in (await request.files).items()}
                data = await request.form.to_dict()  # Other request parameters
                response_text, status = await forward_request_to_telegram(telegram_url, 'POST', data=data, files=files)
            else:
                # For simple POST requests
                incoming_data = await request.get_json()
                response_text, status = await forward_request_to_telegram(telegram_url, 'POST', data=incoming_data)
        else:
            # For GET requests
            incoming_data = request.args.to_dict(flat=True)
            response_text, status = await forward_request_to_telegram(telegram_url, 'GET', data=incoming_data)

        # Return Telegram's response to the requester exactly as received
        return Response(response_text, status=status, content_type='application/json')
    except aiohttp.ClientError as e:
        logging.error(f'Error forwarding request to Telegram: {e}')
        return jsonify({'error': 'Failed to forward request to Telegram'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
