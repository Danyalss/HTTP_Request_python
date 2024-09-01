from flask import Flask, request, Response, jsonify
import requests

app = Flask(__name__)

# شمارنده درخواست‌ها
request_counter = 0

@app.route('/')
def home():
    # محتوای HTML با فاویکن و عنوان پویا
    return Response(f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>requests handled: {request_counter}</title>
        <link rel="icon" href="/static/logo.png" type="image/png">
    </head>
    <body>
        <div style="text-align: center; margin-top: 50px;">
            <h1>Server is running</h1>
            <p>Total requests handled: {request_counter}</p>
        </div>
    </body>
    </html>
    ''', content_type='text/html')

@app.route('/bot<bot_token>/<path:telegram_method>', methods=['POST', 'GET'])
def proxy_to_telegram(bot_token, telegram_method):
    global request_counter
    request_counter += 1  # افزایش شمارنده درخواست‌ها

    # URL کامل برای API تلگرام
    telegram_url = f"https://api.telegram.org/bot{bot_token}/{telegram_method}"

    try:
        # ارسال درخواست به تلگرام
        if request.method == 'POST':
            response = requests.post(telegram_url, data=request.form, files=request.files) if 'multipart/form-data' in request.content_type else requests.post(telegram_url, json=request.json)
        else:
            response = requests.get(telegram_url, params=request.args)
        
        # بازگرداندن پاسخ از تلگرام
        return Response(response.content, status=response.status_code, content_type=response.headers.get('Content-Type'))
    
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to forward request to Telegram: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

