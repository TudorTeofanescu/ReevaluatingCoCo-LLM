# CoCo Analysis: khcfgonjedepfhdepncicddcibcldekp

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/khcfgonjedepfhdepncicddcibcldekp/opgen_generated_files/cs_0.js
Line 467: `window.addEventListener("message",function(e){e.data.code&&("CALL_CENTER_CHECK_EXTENSION"===e.data.code?document.getElementById("call-center-extension-chrome").setAttribute("data-ext","1"):chrome.runtime.sendMessage(e.data))})`

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/khcfgonjedepfhdepncicddcibcldekp/opgen_generated_files/bg.js
Line 965: `callCenterOpen(A.url,!1,A.call_to||"")` leading to `chrome.storage.local.set({callCenterUrl:A})`

**Code:**

```javascript
// Content script - Entry point (cs_0.js Line 467)
window.addEventListener("message", function(e) {
  e.data.code && (
    "CALL_CENTER_CHECK_EXTENSION" === e.data.code ?
      document.getElementById("call-center-extension-chrome").setAttribute("data-ext", "1") :
      chrome.runtime.sendMessage(e.data)  // ← attacker-controlled e.data
  )
});

// Background script - Message handler (bg.js Line 965+)
chrome.runtime.onMessage.addListener(async function(A) {
  var e = (await chrome.storage.local.get(["callCenterNotificationId"]))["callCenterNotificationId"];
  e = e || [];
  A.code && (
    "CALL_CENTER_OPEN" === A.code ?
      callCenterOpen(A.url, !1, A.call_to || "")  // ← attacker-controlled A.url
      : // ... other handlers
  )
});

async function callCenterOpen(A, e, o) {  // A = attacker-controlled URL
  o = o || "";
  const n = (await chrome.storage.local.get(["callCenterUrl"]))["callCenterUrl"];
  var i = (await chrome.storage.local.get(["callCenterWindowId"]))["callCenterWindowId"];

  if (null === n) {
    if (!A) return chrome.action.disable(), void chrome.storage.local.set({callCenterUrl: null});
    chrome.storage.local.set({callCenterUrl: A});  // ← SINK: Stores attacker URL
  }

  // Later creates window with attacker URL
  const n = (await chrome.storage.local.get(["callCenterUrl"]))["callCenterUrl"];
  chrome.windows.create({
    url: n + ("" !== o ? "#call-to=" + o : ""),  // ← Opens attacker URL
    // ...
  });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from malicious webpage

**Attack:**

```javascript
// Malicious webpage sends message to content script
window.postMessage({
  code: "CALL_CENTER_OPEN",
  url: "https://attacker.com/phishing-page"
}, "*");
```

**Impact:** An attacker can force the extension to store an arbitrary URL in chrome.storage.local and then create a new popup window displaying that URL. This enables phishing attacks where the attacker can redirect users to malicious sites that appear to be opened by the legitimate ServiceCall.ai extension. The window is created with `type: "popup"` and can be made fullscreen, making it highly convincing to users who expect the legitimate call center interface.
