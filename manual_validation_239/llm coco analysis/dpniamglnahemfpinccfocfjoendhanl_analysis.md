# CoCo Analysis: dpniamglnahemfpinccfocfjoendhanl

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** Multiple instances of the same pattern (chrome_storage_local_set_sink)

---

## Sink: cs_window_eventListener_OolletEventReq → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dpniamglnahemfpinccfocfjoendhanl/opgen_generated_files/cs_0.js
Line 482: window.addEventListener('OolletEventReq', async function (event) {
Line 483: if (event && event.detail && event.detail.oolletType && event.detail.method) {
Line 488: var msgDetails = {method: event.detail.method, id: event.detail.id, oolletType: event.detail.oolletType, transaction: event.detail.transaction, host: url.host};

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dpniamglnahemfpinccfocfjoendhanl/opgen_generated_files/bg.js
Line 1035: if(message.transaction.type != "entry_function_payload") {
Line 1039: if(message.transaction.function != "0x1::coin::transfer") {
Line 1106: chrome.storage.local.set({transaction: transaction})

**Code:**

```javascript
// Content script (cs_0.js) - Entry point
window.addEventListener('OolletEventReq', async function (event) {
  if (event && event.detail && event.detail.oolletType && event.detail.method) {
    if (event.detail.oolletType == "oolletApiRequest") {
      if ((event.detail.method == "getAccount") || (event.detail.method == "signAndSubmitTransaction")) {
        const url = new URL(window.location.href);
        var msgDetails = {
          method: event.detail.method,
          id: event.detail.id,
          oolletType: event.detail.oolletType,
          transaction: event.detail.transaction,  // ← attacker-controlled
          host: url.host
        };
        sendMessage(msgDetails).then((response) => {
          var respEvent = new CustomEvent("OolletEventResp", {
            detail: { responseMethod: event.detail.method, id: event.detail.id, response }
          });
          window.dispatchEvent(respEvent);
        })
      }
    }
  }
})

// Background script (bg.js) - Message handler
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  switch (message.method) {
    case 'signAndSubmitTransaction':
      if(message.transaction.type != "entry_function_payload") {  // Uses attacker data
        sendResponse({code: 1, name: "LibraError", message: "Transaction type not supported yet"});
        break;
      }
      if(message.transaction.function != "0x1::coin::transfer") {  // Uses attacker data
        sendResponse({code: 1, name: "LibraError", message: "Transaction function not supported yet"});
        break;
      }
      isApprovedUrl(message.host).then((approved) =>{
        if (approved) {
          signAndSubmitTransaction(message.transaction).then((txResults) => {
            sendResponse(txResults);
          });
        }
      });
      return true;
  }
});

function signAndSubmitTransaction(transaction) {
  return new Promise((resolve, reject) => {
    chrome.storage.local.set({transaction: transaction}).then(() => {  // Storage write
      chrome.windows.create({url: "verify.html", type: "popup"}).then((windowResponse) => {
        chrome.storage.local.set({transaction_id: "Transaction rejected"});
        chrome.windows.onRemoved.addListener(function onRemovedListener (windowId){
          if (windowId == windowResponse.id){
            chrome.storage.local.get('transaction_id').then((results) => {
              txResults = results.transaction_id;  // Only reads transaction_id, not original transaction
              resolve({hash: txResults});  // Sends back result, not attacker's input
            });
          }
        });
      });
    });
  });
}
```

**Classification:** FALSE POSITIVE

**Reason:** This is incomplete storage exploitation. The attacker-controlled transaction data is stored via chrome.storage.local.set({transaction: transaction}), but the stored data never flows back to the attacker. The transaction is meant to be read by the extension's own UI (verify.html popup) for user confirmation. Only the result (transaction_id) is sent back via sendResponse, not the original attacker-controlled transaction data. According to the methodology (Rule 2 and False Positive pattern Y), storage poisoning alone without a retrieval path to the attacker is NOT a vulnerability.

---
