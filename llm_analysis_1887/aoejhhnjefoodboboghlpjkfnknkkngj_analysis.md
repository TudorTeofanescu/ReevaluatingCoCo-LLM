# CoCo Analysis: aoejhhnjefoodboboghlpjkfnknkkngj

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/aoejhhnjefoodboboghlpjkfnknkkngj/opgen_generated_files/cs_0.js
Line 498: window.addEventListener('message', function (event) {
Line 499: if (event.source === window && event.data && event.data.type === 'embeddedData') {
Line 501: console.log('Embedded data received by contentScript:', event.data.data);

**Code:**

```javascript
// Content script (cs_0.js) - Line 498
window.addEventListener('message', function (event) {
  if (event.source === window && event.data && event.data.type === 'embeddedData') {
    console.log('Embedded data received by contentScript:', event.data.data);
    chrome.runtime.sendMessage({ action: 'retrieveData', embeddedData: event.data.data }); // ← attacker-controlled
  }
});

// Background script (bg.js) - Line 1138
chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {
    if (message && message.action === 'retrieveData' && message.embeddedData !== undefined) {
        const userId = message.embeddedData; // ← attacker-controlled
        chrome.storage.local.get("pluginLocked", (result) => {
            if (!result.pluginLocked) {
                chrome.storage.local.get("userId", (result) => {
                    if (!result.userId) {
                        chrome.storage.local.set({userId: userId}, function () { // Storage sink
                            console.log('User ID stored:', userId);
                            updateUninstallURL(userId);
                            sendResponse({confirmation: 'dataReceived'});
                            startHistoricalProcessing(userId);
                        });
                    }
                });
            }
        });
    }
    return true;
});
```

**Classification:** FALSE POSITIVE

**Reason:** The content script is restricted by manifest.json to only run on `https://socialtau.qualtrics.com/jfe/*/SV_*` domains. While an attacker controlling that domain could dispatch a custom message event to poison storage, this is incomplete storage exploitation. The stored userId is never read back and sent to an attacker-accessible output (no sendResponse with storage data, no postMessage back to attacker, no fetch to attacker-controlled URL). Storage poisoning alone without a retrieval path that flows back to the attacker is not exploitable per the methodology.
