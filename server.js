addEventListener('fetch', event => {
    event.respondWith(handleRequest(event.request));
  });
  
  const TELEGRAM_API_BASE_URL = 'https://api.telegram.org';
  let requestCounter = 0; // شمارنده درخواست‌ها
  
  async function handleRequest(request) {
    const url = new URL(request.url);
  
    // بررسی اینکه آیا درخواست برای صفحه اصلی است
    if (url.pathname === '/') {
      return new Response(`
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>requests handled: ${requestCounter}</title>
            <link rel="icon" href="https://example.com/logo.png" type="image/png"> <!-- جایگزین با URL واقعی لوگو -->
        </head>
        <body>
            <div style="text-align: center; margin-top: 50px;">
                <h1>Server is running</h1>
                <p>Total requests handled: ${requestCounter}</p>
            </div>
        </body>
        </html>
      `, { headers: { 'Content-Type': 'text/html' } });
    }
  
    // بررسی اینکه آیا درخواست برای متدهای ربات تلگرام است
    const botMatch = url.pathname.match(/^\/bot(.+?)\/(.+)$/);
    if (botMatch) {
      requestCounter++; // افزایش شمارنده درخواست‌ها
  
      const [_, botToken, telegramMethod] = botMatch;
      const telegramUrl = `${TELEGRAM_API_BASE_URL}/bot${botToken}/${telegramMethod}`;
  
      try {
        const requestOptions = {
          method: request.method,
          headers: request.headers
        };
  
        if (request.method === 'POST') {
          const contentType = request.headers.get('Content-Type') || '';
          if (contentType.includes('multipart/form-data')) {
            const formData = await request.formData();
            requestOptions.body = JSON.stringify(Object.fromEntries(formData));
            requestOptions.headers['Content-Type'] = 'application/json';
          } else {
            requestOptions.body = await request.text();
          }
        } else {
          requestOptions.body = null;
        }
  
        const response = await fetch(telegramUrl, requestOptions);
        const responseBody = await response.text();
        return new Response(responseBody, {
          status: response.status,
          headers: { 'Content-Type': response.headers.get('Content-Type') }
        });
      } catch (error) {
        return new Response(JSON.stringify({ error: 'Failed to forward request to Telegram' }), { status: 500 });
      }
    }
  
    // اگر درخواست با هیچ یک از مسیرهای مشخص شده مطابقت نداشته باشد
    return new Response('Not Found', { status: 404 });
  }
  