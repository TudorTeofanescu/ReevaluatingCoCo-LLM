# CoCo Analysis: jkhoiolkabgmmcommldadgndjkjiphep

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2 (both storing message.token and message.user)

---

## Sink 1-2: bg_chrome_runtime_MessageExternal -> chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jkhoiolkabgmmcommldadgndjkjiphep/opgen_generated_files/bg.js
Line 1056	        authToken: message.token,
Line 1057	        userData: message.user,

**Code:**

```javascript
// Background script - External message handler
chrome.runtime.onMessageExternal.addListener(function (
  message,
  sender,
  sendResponse
) {
  console.log("Message received from ConnectDot:", message);
  // Verify sender origin (but we ignore per methodology)
  if (sender.origin !== config.CONNECTDOT_URL) {
    return;
  }

  if (message.type === "auth_success") {
    // Store the token
    chrome.storage.local
      .set({
        authToken: message.token,    // <- attacker-controlled token stored
        userData: message.user,       // <- attacker-controlled user data stored
      })
      .then(() => {
        chrome.runtime.sendMessage({ action: "changePage", page: "exportPage" });
        sendResponse({ success: true });
      });
    return true;
  }
});

// Popup script - Token retrieval and usage
document.addEventListener("DOMContentLoaded", async function () {
  const { authToken } = await chrome.storage.local.get("authToken");

  if (authToken) {
    // Verify token with hardcoded backend API
    const response = await fetch(`${config.API_URL}/users/profile`, {
      headers: {
        Authorization: `Bearer ${authToken}`,  // <- token used in request to hardcoded backend
      },
    });
    // ... (config.API_URL = "https://api-connectdot.fly.dev" or "http://localhost:3000")
  }
});

// Later usage - Upload with token
const uploadResponse = await fetch(
  `${config.API_URL}/users/documents`,  // <- hardcoded backend URL
  {
    method: "PUT",
    headers: {
      Authorization: `Bearer ${authToken}`,  // <- token used in request to hardcoded backend
    },
    body: formData,
  }
);
```

**Classification:** FALSE POSITIVE

**Reason:** While an external attacker (from kore-dun.vercel.app domains) can inject an arbitrary authentication token and user data into storage, the stored token is exclusively used to make authenticated requests to the developer's hardcoded backend URLs (config.API_URL = "https://api-connectdot.fly.dev" or localhost). According to the methodology, data TO hardcoded backend URLs is trusted infrastructure. The attacker can send their own token to authenticate with the developer's backend, but this is an issue with the developer's infrastructure authentication model, not an extension vulnerability. The extension correctly uses the token only for its intended purpose with its own backend services.
