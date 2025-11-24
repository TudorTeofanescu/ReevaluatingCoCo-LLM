# CoCo Analysis: kmjgbjddieihpeglpobkhcnbejiooilh

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_PassAccessToken → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kmjgbjddieihpeglpobkhcnbejiooilh/opgen_generated_files/cs_0.js
Line 572 window.addEventListener("PassAccessToken", function (evt) {
Line 573 chrome.storage.local.set({ accessToken: evt.detail });

**Code:**

```javascript
// getAccessToken.js - Injected script running in webpage context (Lines 1-10)
if (
  window.location.href.includes("https://app.snapp.taxi/") &&
  window.localStorage.accessToken
) {
  const event = new CustomEvent("PassAccessToken", {
    detail: window.localStorage.accessToken,  // Reading from webpage's localStorage
  });

  window.dispatchEvent(event);
}

// contentscript.js - Content script (Lines 571-574)
injectScript(chrome.runtime.getURL("assets/getAccessToken.js"), "body");
window.addEventListener("PassAccessToken", function (evt) {
    chrome.storage.local.set({ accessToken: evt.detail }); // Storing token from webpage
}, false);
```

**Classification:** FALSE POSITIVE

**Reason:** This is incomplete storage exploitation. While a malicious webpage at https://app.snapp.taxi/* could theoretically dispatch a custom "PassAccessToken" event with poisoned data that gets stored in chrome.storage.local, there is no retrieval path for the attacker to access this stored data. The extension only reads the user's own localStorage from the legitimate Snapp taxi website and stores it for its own use (analyzing Snapp rides). Storage poisoning alone without a retrieval mechanism (sendResponse, postMessage back to attacker, or use in attacker-controlled fetch/executeScript) is NOT exploitable according to the methodology. The attacker cannot retrieve the poisoned storage value to complete the attack chain.

---
