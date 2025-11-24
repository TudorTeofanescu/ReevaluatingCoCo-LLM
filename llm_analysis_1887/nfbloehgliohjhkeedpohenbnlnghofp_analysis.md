# CoCo Analysis: nfbloehgliohjhkeedpohenbnlnghofp

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2 (duplicate flows)

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nfbloehgliohjhkeedpohenbnlnghofp/opgen_generated_files/bg.js
Line 1245: storeRetailerAgreement(request.retailer_uid, ALWAYS)
Line 1160: agreements[retailer_uid] = retailer_agreement;

**Code:**

```javascript
// Background script - External message handler (bg.js:1224)
chrome.runtime.onMessageExternal.addListener(
  (request, sender, sendResponse) => {
    if (request.message == 'setRetailerAgreement') {
      storeRetailerAgreement(request.retailer_uid, ALWAYS) // <- retailer_uid from external message
        .then(() => {
          sendResponse({ type: 'success' }); // Only sends success, no data back
        });
    }
  }
);

// Storage function (bg.js:1148-1167)
function storeRetailerAgreement(retailer_uid, status) {
  return new Promise(function(resolve, reject) {
    getAgreements()
      .then((agreements) => {
        let retailer_agreement = agreements[retailer_uid] || {};
        retailer_agreement['status'] = status;
        retailer_agreement['date'] = new Date().toUTCString();
        retailer_agreement['notification_shown'] = false;

        agreements[retailer_uid] = retailer_agreement; // Storage write

        let store = {};
        store[AGREEMENTS_KEY] = agreements;
        chrome.storage.local.set(store); // Sink
        resolve();
      });
  });
}
```

**Classification:** FALSE POSITIVE

**Reason:** Storage poisoning without retrieval path. External messages can write attacker-controlled `retailer_uid` to storage, but there is no code path that reads this stored data and sends it back to the attacker via sendResponse or any other output channel.
