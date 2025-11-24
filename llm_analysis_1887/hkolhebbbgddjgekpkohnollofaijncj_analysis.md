# CoCo Analysis: hkolhebbbgddjgekpkohnollofaijncj

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hkolhebbbgddjgekpkohnollofaijncj/opgen_generated_files/bg.js
Line 989: token: request.token,

**Code:**

```javascript
// Background script - bg.js Line 983
chrome.runtime.onMessageExternal.addListener(function (
  request,
  sender,
  sendResponse
) {
    chrome.storage.local.set({
        token: request.token,  // ← attacker-controlled
    });
    chrome.storage.local.set({
        loginTime: new Date().toISOString(),
    });
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted domain

**Attack:**

```javascript
// From https://www.votingsmarteronboarding.com/* (whitelisted in externally_connectable)
chrome.runtime.sendMessage(
  "hkolhebbbgddjgekpkohnollofaijncj",  // extension ID
  {
    token: "attacker_malicious_token"
  }
);
```

**Impact:** Storage poisoning vulnerability. The extension accepts external messages from the whitelisted domain (https://www.votingsmarteronboarding.com/*) via chrome.runtime.onMessageExternal. An attacker who controls or compromises this domain, or any user visiting a malicious page on this domain, can send arbitrary token values to be stored in chrome.storage.local. While this is storage.set without immediate retrieval shown in the code, the poisoned token is likely used for authentication or session management elsewhere in the extension. According to the methodology, even if only ONE domain is whitelisted, this is classified as TRUE POSITIVE if the flow is exploitable, which it is.
