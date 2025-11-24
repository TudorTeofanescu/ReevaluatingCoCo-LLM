# CoCo Analysis: ehhfanchmgnccanehpebglmjodahjjbd

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: document_eventListener_tokenFound → chrome_storage_local_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ehhfanchmgnccanehpebglmjodahjjbd/opgen_generated_files/cs_1.js
Line 467	document.addEventListener("tokenFound", function(event) {
Line 469	var tokenValue = event.detail.token;
```

**Code:**

```javascript
// Content script (signInContent.js) - Lines 467-479
document.addEventListener("tokenFound", function(event) {
    var tokenValue = event.detail.token; // ← potentially attacker-controlled
    jwtToken = tokenValue;
    chrome.storage.local.set({ jwtToken: jwtToken }, function() {
      console.log('Token saved.' + jwtToken);
      chrome.runtime.sendMessage({ closePopup: true }, function(response) {
        if (response.popupClosed) {
          console.log("Popup window closed");
        }
      });
    });
});

// Storage retrieval (content.js) - Lines 544-553
chrome.storage.local.get(['jwtToken'], function(result) {
  if (result.jwtToken) {
    jwtToken = result.jwtToken;
    resolve(true);
  }
});

// Token used in fetch to hardcoded backend - Lines 558-564
fetch("https://municode.ai/isAuth", {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${jwtToken}`, // ← poisoned token sent to backend
  },
  credentials: 'include',
})
```

**Manifest content_scripts:**
```json
{
  "matches": ["https://municode.ai/loginChrome"],
  "js": ["signInContent.js"]
}
```

**Classification:** FALSE POSITIVE

**Reason:** This is a false positive for two reasons: (1) The event listener in signInContent.js only runs on the developer's own domain `https://municode.ai/loginChrome` as specified in manifest.json content_scripts matches. This is NOT exploitable by external attackers - it's part of the extension's internal authentication workflow on its own trusted domain. (2) Even if the token storage could be poisoned, the complete exploitation chain shows the stored token is retrieved and sent to the hardcoded backend URL `https://municode.ai/` (lines 558, 614). Per methodology, data flowing to hardcoded developer backend URLs is considered trusted infrastructure, not an extension vulnerability.
