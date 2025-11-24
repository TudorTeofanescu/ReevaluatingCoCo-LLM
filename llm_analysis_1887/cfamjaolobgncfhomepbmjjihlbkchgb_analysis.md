# CoCo Analysis: cfamjaolobgncfhomepbmjjihlbkchgb

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: storage_local_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cfamjaolobgncfhomepbmjjihlbkchgb/opgen_generated_files/bg.js
Line 751: CoCo framework code (storage_local_get_source definition)
Line 1085: `permissions: result['registered'] ? 'granted' : 'default'`

**Code:**

```javascript
// Background script (bg.js) - Lines 1081-1092
chrome.runtime.onMessageExternal.addListener(function(request, sender, sendResponse) {
    if (request == 'permissions') {
        chrome.storage.local.get("registered", (result) => {
            sendResponse({
                permissions: result['registered'] ? 'granted' : 'default', // ← storage data sent to external caller
                deviceToken: result['registered'] // ← storage data sent to external caller
            })
        })
    }

    return true;
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted domains

**Attack:**

```javascript
// From any page on *.integromat.com (whitelisted in externally_connectable):
chrome.runtime.sendMessage(
    'cfamjaolobgncfhomepbmjjihlbkchgb', // Extension ID
    'permissions',
    function(response) {
        console.log("Leaked data:", response);
        // response.permissions contains registration status
        // response.deviceToken contains the device token
    }
);
```

**Impact:** Information disclosure vulnerability. An attacker on any integromat.com subdomain can retrieve sensitive stored data including the device registration status and device token. This leaks internal extension state and potentially sensitive authentication tokens to external websites, which could be used for unauthorized push notifications or tracking.
