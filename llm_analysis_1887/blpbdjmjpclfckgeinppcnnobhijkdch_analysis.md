# CoCo Analysis: blpbdjmjpclfckgeinppcnnobhijkdch

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 4 (all the same pattern, different fields)

---

## Sink: cs_window_eventListener_tokenChanged → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/blpbdjmjpclfckgeinppcnnobhijkdch/opgen_generated_files/cs_1.js
Line 467   window.addEventListener("tokenChanged", (event) => {
Line 468   const newToken = event.detail;
Line 470   hiyr_access_token: newToken.access_token,
Line 471   hiyr_refresh_token: newToken.refresh_token,
Line 472   hiyr_token_expiry: newToken.access_token_expires_at,
Line 473   hiyr_refresh_token_expiry: newToken.refresh_token_expires_at,

**Code:**

```javascript
// Content script (updateTokenContentScript.js) - Lines 467-475
window.addEventListener("tokenChanged", (event) => {
  const newToken = event.detail; // ← attacker-controlled via dispatchEvent
  chrome.storage.local.set({
    hiyr_access_token: newToken.access_token,
    hiyr_refresh_token: newToken.refresh_token,
    hiyr_token_expiry: newToken.access_token_expires_at,
    hiyr_refresh_token_expiry: newToken.refresh_token_expires_at,
  });
});
```

**Classification:** FALSE POSITIVE

**Reason:** Storage poisoning without complete exploitation chain. While the content script runs on `<all_urls>` and any webpage can dispatch a custom "tokenChanged" event with malicious token data (event.detail), the poisoned authentication tokens are stored in chrome.storage.local but never retrieved back to the attacker. The extension UI (index.js) may read these tokens internally, but there is no path for the attacker to retrieve the stored values via sendResponse, postMessage, or any attacker-accessible mechanism. According to the methodology, storage poisoning alone without retrieval to the attacker is NOT exploitable.
