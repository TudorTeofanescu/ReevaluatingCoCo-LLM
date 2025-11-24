# CoCo Analysis: limjglkioeenlejbdikfeeecgmigbmmd

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_SendTokenToExtension → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/limjglkioeenlejbdikfeeecgmigbmmd/opgen_generated_files/cs_0.js
Line 674: `window.addEventListener("SendTokenToExtension", function (e) {`
Line 677: `e.detail,`
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/limjglkioeenlejbdikfeeecgmigbmmd/opgen_generated_files/bg.js
Line 984: `if (request.token) {`

**Code:**

```javascript
// Content script - cs_0.js (runs on <all_urls>)
window.addEventListener("SendTokenToExtension", function (e) {
    chrome.runtime.sendMessage(
      "limjglkioeenlejbdikfeeecgmigbmmd",
      e.detail,  // ← attacker-controlled via webpage event
      function (response) {
      }
    );
});

// Background script - bg.js
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.token) {
    chrome.storage.local.set({ 'token': request.token }, function() {  // ← stores attacker data
      if (chrome.runtime.lastError) {
        sendResponse({status: 'Error saving token', error: chrome.runtime.lastError});
      } else {
        sendResponse({status: 'Token received and saved'});  // ← confirms storage to attacker
      }
    });
  }
  return true;
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event listener (window.addEventListener)

**Attack:**

```javascript
// Malicious webpage injects arbitrary token into extension storage
var maliciousToken = "attacker_controlled_jwt_token_12345";
var event = new CustomEvent("SendTokenToExtension", {
    detail: { token: maliciousToken }
});
window.dispatchEvent(event);

// Extension stores the malicious token and sends confirmation back
```

**Impact:** Storage poisoning with attacker confirmation. A malicious webpage can inject arbitrary token values into the extension's storage. The extension confirms successful storage via sendResponse, allowing the attacker to verify the attack succeeded. This enables:

1. **Token injection:** Attacker can plant malicious authentication tokens
2. **Session hijacking:** If the stored token is later used for authentication, attacker gains unauthorized access
3. **Data manipulation:** Attacker can control application state by poisoning stored credentials

The extension has storage permission (manifest.json line 8) and runs content scripts on <all_urls> (line 24), making this exploitable from any webpage the user visits.
