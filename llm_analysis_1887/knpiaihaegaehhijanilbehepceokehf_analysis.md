# CoCo Analysis: knpiaihaegaehhijanilbehepceokehf

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 5 (all cs_window_eventListener_message → chrome_storage_local_set_sink)

---

## Sink 1: cs_window_eventListener_message → chrome_storage_local_set_sink (event.data)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/knpiaihaegaehhijanilbehepceokehf/opgen_generated_files/cs_0.js
Line 486: `window.addEventListener("message", (event) => {`
Line 490: `if (event.data.type && (event.data.type == "UNICORN_WALLET_SEND")) {`

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/knpiaihaegaehhijanilbehepceokehf/opgen_generated_files/bg.js
Line 1001: `var valueString = JSON.stringify(data);`

**Code:**

```javascript
// Content script (cs_0.js) - Lines 486-507
window.addEventListener("message", (event) => {
    if (event.source != window) {
        return;
    }
    if (event.data.type && (event.data.type == "UNICORN_WALLET_SEND")) {  // ← attacker-controlled
        chrome.runtime.sendMessage({ type: "sendTxn", data: event.data }, function (response) {
            console.log("from background" + response);
        });
    }
    else if (event.data.type && (event.data.type == "UNICORN_WALLET_ACCOUNT")) {
        chrome.runtime.sendMessage({ type: "getAccount", data: event.data }, function (response) {
            console.log("from background" + response);
        });
    }
    else if (event.data.type && (event.data.type == "UNICORN_WALLET_TX")) {
        chrome.runtime.sendMessage({ type: "getTx", data: event.data }, function (response) {
            console.log("from background" + response);
        });
    }
}, false);

// Background script (bg.js) - Lines 971-1025
chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
    if (request.type === "sendTxn") {
        sendResponse(true);
        prepareSendTxnStorage(request, sender);  // ← stores data
    }
    else if (request.type === "getAccount") {
        sendResponse(true);
        prepareGetAccountStorage(request, sender);  // ← stores data
    }
    else if (request.type === "getTx") {
        sendResponse(true);
        prepareGetTxStorage(request, sender);  // ← stores data
    }
    return true;
});

const prepareSendTxnStorage = (request, sender) => {
    var data = request.data;  // ← attacker-controlled
    var valueString = JSON.stringify(data);
    chrome.storage.local.set({ "sendTxn": valueString }, function () {  // ← storage sink
        chrome.windows.create({ url: 'index.html', type: "popup", height: 600, width: 375 });
        // Opens popup for user to approve/reject transaction
    });
};

const prepareGetAccountStorage = (request, sender) => {
    var data = request.data;  // ← attacker-controlled
    var domainName = data.domain;
    var valueString = JSON.stringify({ domain: domainName, tabId: sender.tab.id });
    chrome.storage.local.set({ "getAccount": valueString }, function () {  // ← storage sink
        chrome.windows.create({ url: 'index.html', type: "popup", height: 600, width: 375 });
    });
};

const prepareGetTxStorage = (request, sender) => {
    var data = request.data;  // ← attacker-controlled
    var domainName = data.domain;
    var address = data.address;
    var valueString = JSON.stringify({ domain: domainName, tabId: sender.tab.id, address: address });
    chrome.storage.local.set({ "getTx": valueString }, function () {  // ← storage sink
        chrome.windows.create({ url: 'index.html', type: "popup", height: 600, width: 375 });
    });
};
```

**Classification:** FALSE POSITIVE

**Reason:** Incomplete storage exploitation - storage poisoning only without retrieval path. The flow is: webpage postMessage → content script → background → chrome.storage.local.set. However, there is NO code path where the stored data is retrieved (storage.get) and sent back to the attacker via sendResponse, postMessage, or used in a vulnerable operation. The stored data is only used internally by the extension's popup (index.html) where the user must approve transactions. The attacker cannot retrieve the poisoned storage values. Per the methodology: "Storage poisoning alone (storage.set without retrieval) is NOT exploitable! The stored value MUST flow back to the attacker through sendResponse, postMessage, or be used in a subsequent vulnerable operation to be TRUE POSITIVE."

---

## Sinks 2-5: Same vulnerability pattern

**CoCo Trace:** Multiple flows with same pattern (event.data.type, event.data.domain, event.data.address)

**Classification:** FALSE POSITIVE

**Reason:** All sinks follow the same pattern - storage poisoning without retrieval path back to attacker. The extension stores attacker-controlled data but never retrieves it in a way accessible to the attacker.
