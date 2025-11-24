# CoCo Analysis: ljglebelbpllfdejeekfgpidbpcbpmff

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2 (both part of same flow)

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ljglebelbpllfdejeekfgpidbpcbpmff/opgen_generated_files/bg.js
Line 1131: if (request.session) {
Line 1138: accessToken: userSession.accessToken.jwtToken,
Line 1139: refreshToken: userSession.refreshToken.token
```

**Code:**
```javascript
// Background script - External message handler (bg.js)
chrome.runtime.onMessageExternal.addListener(
  (request, sender, sendResponse) => {
    console.log("INFO:: Got a message to the background from website", request);
    if (request.session) { // ← attacker-controlled
      sendResponse({
        success: true,
        message: "Token has been received by background"
      });
      let userSession = request.session; // ← attacker-controlled
      chrome.storage.local.set({
        accessToken: userSession.accessToken.jwtToken, // ← attacker-controlled
        refreshToken: userSession.refreshToken.token   // ← attacker-controlled
      }).then(() => {
        console.log(
          "INFO (SUCCESS):: Set session token in the background session data"
        );
      }).catch((error) => {
        console.log(
          "ERROR:: got an error while setting token data in local storage",
          error
        );
      });
    }
  }
);
```

**Classification:** FALSE POSITIVE

**Reason:** While the extension accepts external messages and stores attacker-controlled data via `chrome.runtime.onMessageExternal`, this is an incomplete storage exploitation chain. The stored tokens are later retrieved and sent to hardcoded backend URLs (BACKEND_URL for verification and AWS Cognito for token refresh), not to attacker-controlled destinations. According to the methodology, "Hardcoded backend URLs are still trusted infrastructure" and "storage.get → fetch(hardcodedBackendURL)" is a FALSE POSITIVE pattern. The attacker cannot retrieve the poisoned values back, as the internal message handler (chrome.runtime.onMessage) that retrieves tokens is only accessible to the extension's own components, not external attackers. This is storage poisoning without a retrieval path to the attacker.
