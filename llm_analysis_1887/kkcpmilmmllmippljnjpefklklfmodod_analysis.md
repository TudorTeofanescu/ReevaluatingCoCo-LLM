# CoCo Analysis: kkcpmilmmllmippljnjpefklklfmodod

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kkcpmilmmllmippljnjpefklklfmodod/opgen_generated_files/bg.js
Line 1036: chrome.storage.local.set({ authToken: request.token });

**Code:**

```javascript
// Background script

// External message handler - attacker can set authToken
chrome.runtime.onMessageExternal.addListener((request, sender, sendResponse) => {
    if (request.type === 'SET_AUTH_TOKEN') {
        chrome.storage.local.set({ authToken: request.token }); // ← storage write
        sendResponse({ success: true });
    }
    return true;
});

// Function that retrieves and uses the authToken
function handleSaveVideo(url, reviewDeadline) {
    return __awaiter(this, void 0, void 0, function* () {
        const { authToken: storedToken } = yield chrome.storage.local.get('authToken'); // ← storage read

        if (!storedToken) {
            chrome.tabs.create({ url: config_1.AUTH_ROUTES.signin });
            return;
        }

        // Uses token to verify with hardcoded backend
        const verifyResponse = yield fetch(config_1.AUTH_ROUTES.verify, { // ← https://getsavy.ai/api/auth/verify
            headers: {
                'Authorization': `Bearer ${storedToken}` // ← poisoned token sent to hardcoded backend
            }
        });

        if (!verifyResponse.ok) {
            chrome.storage.local.remove('authToken');
            chrome.tabs.create({ url: config_1.AUTH_ROUTES.signin });
            return;
        }

        // Uses token to save video with hardcoded backend
        const saveResponse = yield fetch(config_1.AUTH_ROUTES.save, { // ← https://getsavy.ai/api/video/save
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${storedToken}` // ← poisoned token sent to hardcoded backend
            },
            body: JSON.stringify({ url, reviewDeadline }),
        });

        // ...
    });
}

// Configuration - hardcoded backend URLs
exports.WEB_URL = "https://getsavy.ai";
exports.AUTH_ROUTES = {
    signin: `${exports.WEB_URL}/signin`,
    verify: `${exports.WEB_URL}/api/auth/verify`, // ← hardcoded backend
    save: `${exports.WEB_URL}/api/video/save`, // ← hardcoded backend
};
```

**Manifest permissions:**
```json
{
  "externally_connectable": {
    "matches": [
      "*://*.getsavy.ai/*",
      "https://getsavy.ai/*"
    ]
  },
  "host_permissions": [
    "https://*.youtube.com/*",
    "https://getsavy.ai/*"
  ]
}
```

**Classification:** FALSE POSITIVE

**Reason:** This is an incomplete storage exploitation chain involving a hardcoded backend URL (trusted infrastructure). While an attacker controlling a page on `getsavy.ai` can poison the `authToken` in chrome.storage.local via the external message handler, the poisoned token only flows back to the developer's own hardcoded backend URLs:

1. Storage write: `attacker → storage.set({ authToken: ... })`
2. Storage read: `storage.get('authToken') → storedToken`
3. Data destination: `fetch('https://getsavy.ai/api/auth/verify', { Authorization: Bearer ${storedToken} })`

Per the methodology, this is explicitly classified as FALSE POSITIVE:
- "Storage to hardcoded backend: `storage.get → fetch(hardcodedBackendURL)` (trusted destination, not attacker-accessible)"

The poisoned data flows to `https://getsavy.ai/*`, which is the developer's own trusted backend infrastructure. The attacker cannot retrieve the poisoned value back to an attacker-controlled destination - it only gets sent to getsavy.ai's servers. Compromising the developer's backend infrastructure is a separate infrastructure security issue, not an extension vulnerability. For this to be a TRUE POSITIVE, the stored authToken would need to flow back to the attacker (via sendResponse, postMessage, or a fetch to an attacker-controlled URL), which does not occur here.
