from quart import Quart, request, jsonify
import aiohttp
import logging

app = Quart(__name__)

# تنظیمات لاگ‌گیری
logging.basicConfig(filename='requests.log', level=logging.INFO, format='%(asctime)s - %(message)s')

async def forward_request_to_telegram(telegram_url, method, data=None, files=None):
    async with aiohttp.ClientSession() as session:
        if method == 'POST':
            if files:
                # ارسال درخواست POST با فایل‌ها
                form_data = aiohttp.FormData()
                for key, (filename, file_content, content_type) in files.items():
                    form_data.add_field(key, file_content, filename=filename, content_type=content_type)
                async with session.post(telegram_url, data=form_data) as response:
                    return await response.json()
            else:
                # ارسال درخواست POST ساده
                async with session.post(telegram_url, json=data) as response:
                    return await response.json()
        else:
            # ارسال درخواست GET
            async with session.get(telegram_url, params=data) as response:
                return await response.json()

@app.route('/bot<bot_token>/<path:telegram_method>', methods=['POST', 'GET'])
async def proxy_to_telegram(bot_token, telegram_method):
    # ثبت جزئیات درخواست
    logging.info(f'Received request for bot token: {bot_token}, method: {telegram_method}, data: {await request.get_data()}')

    # URL کامل به سرور تلگرام
    telegram_url = f"https://api.telegram.org/bot{bot_token}/{telegram_method}"

    # ارسال درخواست به تلگرام
    try:
        if request.method == 'POST':
            if 'multipart/form-data' in request.content_type:  # چک کردن اگر درخواست شامل فایل باشد
                files = {key: (file.filename, await file.read(), file.content_type) for key, file in (await request.files).items()}
                data = await request.form.to_dict()  # بقیه پارامترهای درخواست
                response = await forward_request_to_telegram(telegram_url, 'POST', data=data, files=files)
            else:
                # برای درخواست‌های POST ساده
                incoming_data = await request.get_json()
                response = await forward_request_to_telegram(telegram_url, 'POST', data=incoming_data)
        else:
            # برای درخواست‌های GET
            incoming_data = request.args.to_dict(flat=True)
            response = await forward_request_to_telegram(telegram_url, 'GET', data=incoming_data)

        # برگرداندن پاسخ تلگرام به درخواست کننده
        return jsonify(response)
    except aiohttp.ClientError as e:
        logging.error(f'Error forwarding request to Telegram: {e}')
        return jsonify({'error': 'Failed to forward request to Telegram'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
