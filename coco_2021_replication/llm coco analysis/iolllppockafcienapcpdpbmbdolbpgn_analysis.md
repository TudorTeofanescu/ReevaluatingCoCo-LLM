# CoCo Analysis: iolllppockafcienapcpdpbmbdolbpgn

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 17 (multiple variations of the same flow pattern)

---

## Sink: document_eventListener_extensions_request → XMLHttpRequest_url_sink

**CoCo Trace:**
```
$FilePath$/media/data2/jianjia/extension_data/unzipped_extensions/iolllppockafcienapcpdpbmbdolbpgn/opgen_generated_files/cs_0.js
Line 578	function allowedExtensionsRequest(param) {
	param
Line 579	    if(param && param.detail && param.detail.domain) {
	param.detail.domain
$FilePath$/media/data2/jianjia/extension_data/unzipped_extensions/iolllppockafcienapcpdpbmbdolbpgn/opgen_generated_files/bg.js
Line 894	                    url = url.replace("%domain", encodeURIComponent(request.detail.domain));
	encodeURIComponent(request.detail.domain)
Line 925	        var url = partialUrl.replace("%port", ports[portIndex]);
	partialUrl.replace("%port", ports[portIndex])
```

**Code:**

```javascript
// Content script (cs_0.js) - Entry point
document.addEventListener("extensions_request", allowedExtensionsRequest, false);

function allowedExtensionsRequest(param) {
    if(param && param.detail && param.detail.domain) {
        chrome.runtime.sendMessage({
            request: "allowed_extensions",
            detail: param.detail // ← attacker-controlled
        }, function(resp) {
            // response handling
        });
    }
}

// Background script (bg.js)
var baseUrl = "http://localhost%port"; // ← hardcoded localhost backend
var operations = {
    extensions: "/api/component/extension/allowed?domain=%domain",
    // ...other endpoints
};

chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if(request.request) {
        switch(request.request) {
            case "allowed_extensions":
                if(request.detail.domain) {
                    var url = baseUrl + operations.extensions;
                    url = url.replace("%domain", encodeURIComponent(request.detail.domain));
                    sendRequest(url, 0, sendResponse); // ← sends to localhost
                }
                return true;
            // ... other cases
        }
    }
});

function sendRequest(partialUrl, portIndex, callback) {
    var url = partialUrl.replace("%port", ports[portIndex]);
    var xhtp = new XMLHttpRequest();
    xhtp.open("GET", url, true); // ← XHR to localhost
    // ... request handling
}
```

**Classification:** FALSE POSITIVE

**Reason:** All detected flows (extensions_request, open_document_request, document_progress_request, sign_document_request) follow the same pattern: attacker-controlled data from DOM events flows to XMLHttpRequest, BUT the baseUrl is hardcoded to "http://localhost%port" (developer's trusted local backend). According to the methodology, flows involving hardcoded backend URLs are FALSE POSITIVES - the developer trusts their own infrastructure, and compromising it is an infrastructure issue, not an extension vulnerability. The attacker can control parameters sent to localhost, but cannot redirect requests to attacker-controlled servers.

---

## All Other Sinks (open_document_request, document_progress_request, sign_document_request → XMLHttpRequest_url_sink)

**Classification:** FALSE POSITIVE

**Reason:** Same pattern as above - all flows send attacker-controlled data (token, domain, fileName, signType, taskId, actionId) to the hardcoded localhost backend. This is trusted infrastructure, not attacker-accessible.
