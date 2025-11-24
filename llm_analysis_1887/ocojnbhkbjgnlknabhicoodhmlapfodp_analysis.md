# CoCo Analysis: ocojnbhkbjgnlknabhicoodhmlapfodp

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink (accessToken)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ocojnbhkbjgnlknabhicoodhmlapfodp/opgen_generated_files/bg.js
Line 987	      if (request.accessToken && request.refreshToken) {
	request.accessToken

**Code:**

```javascript
// Background script - External message listener (bg.js, line 985)
chrome.runtime.onMessageExternal.addListener((request, sender, sendResponse) => {
  if (request.message == 'from_speak_app_auth') {
    if (request.accessToken && request.refreshToken) {
      // set user's access token and refresh token in extension's localstorage
      chrome.storage.sync.set(
        {
          accessToken: request.accessToken, // ← attacker-controlled
          refreshToken: request.refreshToken, // ← attacker-controlled
        },
        () => {},
      );
      user.accessToken = request.accessToken;
      user.refreshToken = request.refreshToken;
    }
    sendResponse({
      sender: 'Chrome extension',
      data: 'user accessToken received successfully',
    });
  }
});
```

**Classification:** FALSE POSITIVE

**Reason:** Storage poisoning without retrieval path back to attacker. While an attacker can poison the stored tokens via chrome.runtime.onMessageExternal (from whitelisted domains per manifest: *://*.speakai.co/*, *://speakai.co//*, http://localhost:4200/*), there is no mechanism for the attacker to retrieve these stored values. The tokens are only used internally to authenticate with the developer's backend (app.speakai.co, dev.speakai.co, localhost:4200), which is trusted infrastructure. Poisoning the tokens would disrupt the extension's functionality but doesn't provide exploitable impact to the attacker.

---

## Sink 2: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink (refreshToken)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ocojnbhkbjgnlknabhicoodhmlapfodp/opgen_generated_files/bg.js
Line 987	      if (request.accessToken && request.refreshToken) {
	request.refreshToken

**Classification:** FALSE POSITIVE

**Reason:** Same as Sink 1. Storage poisoning without retrieval path. No exploitable impact.
