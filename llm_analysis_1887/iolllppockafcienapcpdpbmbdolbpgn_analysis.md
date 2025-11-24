# CoCo Analysis: iolllppockafcienapcpdpbmbdolbpgn

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 16 (all same vulnerability pattern)

---

## Sink: document_eventListener_* → XMLHttpRequest_url_sink

**CoCo Trace:**
Multiple flows detected from various document event listeners:
- document_eventListener_extensions_request
- document_eventListener_open_document_request
- document_eventListener_document_progress_request
- document_eventListener_sign_document_request

All flow to XMLHttpRequest with attacker-controlled parameters in URL.

**Code:**

```javascript
// Content script (cs_0.js) - Entry points via custom DOM events
document.addEventListener("version_request", versionRequest, false);
document.addEventListener("extensions_request", allowedExtensionsRequest, false);
document.addEventListener("open_document_request", openDocumentRequest, false);
document.addEventListener("document_progress_request", documentProgressRequest, false);
document.addEventListener("sign_document_request", signRequest, false);

// Example handler
function allowedExtensionsRequest(param) {
  if(param && param.detail && param.detail.domain) {
    chrome.runtime.sendMessage({
      request: "allowed_extensions",
      detail: param.detail  // ← attacker-controlled
    }, function(resp) {
      // Send response back to page
    });
  }
}

// Background script (bg.js) - Message handler
var baseUrl = "http://localhost%port";  // ← localhost only
var ports = [ ":15100", ":15101" ];

chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  if(request.request) {
    switch(request.request) {
      case "allowed_extensions":
        if(request.detail.domain) {
          var url = baseUrl + operations.extensions;
          url = url.replace("%domain", encodeURIComponent(request.detail.domain));
          sendRequest(url, 0, sendResponse);  // ← XMLHttpRequest to localhost
        }
        return true;
      case "open_document":
        var url = baseUrl + operations.open;
        url = url.replace("%token", request.detail.token)
             .replace("%domain", encodeURIComponent(request.detail.domain))
             .replace("%fileName", request.detail.fileName);
        sendRequest(url, 0, sendResponse);  // ← XMLHttpRequest to localhost
        return true;
      // More cases...
    }
  }
});

function sendRequest(partialUrl, portIndex, callback) {
  var url = partialUrl.replace("%port", ports[portIndex]);
  var xhtp = new XMLHttpRequest();
  xhtp.open("GET", url, true);  // ← Always GET to localhost:15100 or :15101
  xhtp.send();
}
```

**Classification:** FALSE POSITIVE

**Reason:** Hardcoded backend URL (trusted infrastructure). While attacker-controlled data flows into URL parameters, the base URL is hardcoded to localhost with specific ports (15100, 15101). This matches False Positive Pattern X from methodology:

> "Hardcoded Backend URLs (Trusted Infrastructure): Data TO hardcoded backend: fetch("https://api.myextension.com", {body: attackerData})"

**Analysis:**
1. **Hardcoded destination:** All XMLHttpRequest calls go to `http://localhost:15100` or `http://localhost:15101`
2. **Trusted infrastructure:** These are the extension's own local native component servers
3. **Query parameters only:** Attacker can only control query parameters (domain, token, fileName, etc.), not the destination host
4. **Design pattern:** Extension is designed to communicate with local 4th Office desktop application via localhost API

Per methodology:
> "Hardcoded backend URLs are still trusted infrastructure: Developer trusts their own infrastructure; compromising it is infrastructure issue, not extension vulnerability"

While an attacker on any webpage can dispatch custom DOM events with controlled parameters, they can only send those parameters to the developer's own localhost service (4th Office native app). The attacker cannot:
- Change the destination to their own server
- Make requests to arbitrary internal network hosts
- Exfiltrate data to external domains

This is internal communication between browser extension and local desktop application, which is the intended design. The attack surface is limited to potentially exploiting bugs in the localhost service itself, which is separate from extension vulnerabilities.

**Note:** All 16 detections are variations of the same pattern (different event types and parameters), all targeting the same hardcoded localhost backend.
