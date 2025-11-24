# CoCo Analysis: eannaomdbmcakllbmhhaiaekahjdhffa

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/eannaomdbmcakllbmhhaiaekahjdhffa/opgen_generated_files/bg.js
Line 973: if (request.jwt)
Line 975: chrome.storage.sync.set({ token: request.jwt }, function () {})

**Code:**

```javascript
// Background script - External message handler (lines 972-982 in bg.js)
chrome.runtime.onMessageExternal.addListener((request, sender, sendResponse) => {
    if (request.jwt) {
        try {
            chrome.storage.sync.set({ token: request.jwt }, function () {
                // ← attacker-controlled JWT stored
            });
            sendResponse({ success: true, message: 'Token has been received' });
        } catch (err) {
            sendResponse({ error: true, message: 'Something went wrong' })
        }
    }
});

// Popup script (popup_new.js) - Reads token and uses in API calls
async function mainFuction() {
  var p = new Promise(function (resolve, reject) {
    chrome.storage.sync.get("token", function (res) {
      resolve(res);
    });
  });
  const token = await p;
  return token;
}

function getConfig(targetMethod, token, body) {
  return {
    method: targetMethod,
    headers: {
      Authorization: token.access ? "JWT " + token.access : null, // ← Poisoned token used
      "Content-Type": "application/json",
      accept: "application/json",
    },
    body: JSON.stringify(body),
  };
}

// Token used in API calls to hardcoded backend
callAPI("api/check-chrome-login/", { isrefresh: false, token: token })
fetch(`${full_url}api/new-recording-request`, getConfig("POST", token, body))
// full_url = "https://app.screenjar.com/"
```

**Classification:** FALSE POSITIVE

**Reason:** Incomplete storage exploitation - poisoned data flows TO hardcoded backend, not back to attacker.

The flow is:
1. Attacker (from whitelisted domain *.screenjar.com) stores malicious JWT via onMessageExternal
2. Popup reads the JWT from storage
3. JWT is used in Authorization header for fetch() calls to hardcoded backend `https://app.screenjar.com/`

According to the methodology, "Data TO hardcoded backend: `attacker-data → fetch("https://api.myextension.com", {body: attackerData})`" is FALSE POSITIVE because the attacker's data goes to the developer's trusted infrastructure, not back to the attacker.

The poisoned JWT is used to authenticate requests to app.screenjar.com (the developer's backend), but:
- The data does NOT flow back to the attacker via sendResponse or postMessage
- The data goes TO the hardcoded backend (trusted infrastructure)
- The attacker already controls *.screenjar.com (the whitelisted domain), so they control both the injection point and the destination

This is not a complete storage exploitation chain. For TRUE POSITIVE, the stored data must flow back to the attacker through sendResponse, postMessage, or be used in a subsequent vulnerable operation that the attacker can observe/control. Using the poisoned data in requests to the developer's own backend is not exploitable from the extension security perspective - it's an infrastructure trust issue.
