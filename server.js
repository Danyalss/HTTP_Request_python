addEventListener('fetch', event => {
    event.respondWith(handleRequest(event.request));
  });
  
  const TELEGRAM_API_BASE_URL = 'https://api.telegram.org';
  let requestCounter = 0; // Counter to keep track of handled requests
  
  async function handleRequest(request) {
    const url = new URL(request.url);
  
    // Check if the request is to the home page
    if (url.pathname === '/') {
      return new Response(
        `
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>requests handled: ${requestCounter}</title>
            <link rel="icon" href="https://example.com/logo.png" type="image/png"> <!-- Replace with your actual logo URL -->
        </head>
        <body>
            <div style="text-align: center; margin-top: 50px;">
                <h1>Server is running</h1>
                <p>Total requests handled: ${requestCounter}</p>
            </div>
        </body>
        </html>
        `,
        { headers: { 'Content-Type': 'text/html' } }
      );
    }
  
    // Check if the request is for a Telegram bot method
    const botMatch = url.pathname.match(/^\/bot(.+?)\/(.+)$/);
    if (botMatch) {
      requestCounter++; // Increment the request counter
  
      const botToken = botMatch[1];
      const telegramMethod = botMatch[2];
  
      // Construct the Telegram API URL
      const telegramUrl = `${TELEGRAM_API_BASE_URL}/bot${botToken}/${telegramMethod}`;
  
      try {
        let response;
  
        if (request.method === 'POST') {
          if (request.headers.get('content-type').includes('multipart/form-data')) {
            // Process multipart form data
            const formData = await request.formData();
            const formDataObj = {};
  
            // Convert FormData to JSON object
            formData.forEach((value, key) => {
              if (value instanceof File) {
                // Handle file uploads here if needed
                formDataObj[key] = value; // Not handling file uploads in this example
              } else {
                formDataObj[key] = value;
              }
            });
  
            // Forward the request to Telegram
            response = await fetch(telegramUrl, {
              method: 'POST',
              body: JSON.stringify(formDataObj), // Send JSON object instead of FormData
              headers: { 'Content-Type': 'application/json' }
            });
          } else {
            // Forward simple POST requests
            const requestBody = await request.text(); // Read the body as text
            response = await fetch(telegramUrl, {
              method: 'POST',
              body: requestBody,
              headers: request.headers
            });
          }
        } else {
          // For GET requests
          const incomingData = new URLSearchParams(url.search).toString();
          response = await fetch(telegramUrl, {
            method: 'GET',
            headers: request.headers
          });
        }
  
        const responseData = await response.text();
        return new Response(responseData, {
          status: response.status,
          headers: { 'Content-Type': response.headers.get('content-type') }
        });
      } catch (error) {
        return new Response(JSON.stringify({ error: 'Failed to forward request to Telegram' }), { status: 500 });
      }
    }
  
    // If the request doesn't match any known routes
    return new Response('Not Found', { status: 404 });
  }
  