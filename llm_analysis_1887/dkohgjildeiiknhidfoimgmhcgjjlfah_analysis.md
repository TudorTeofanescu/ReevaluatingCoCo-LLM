# CoCo Analysis: dkohgjildeiiknhidfoimgmhcgjjlfah

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_OpenPopup -> chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dkohgjildeiiknhidfoimgmhcgjjlfah/opgen_generated_files/cs_0.js
Line 475: window.addEventListener('OpenPopup', function(evt) {
Line 476: chrome.runtime.sendMessage({ type: 'open', data: evt.detail});

**Code:**

```javascript
// Content script (cs_0.js Line 475-476)
window.addEventListener('OpenPopup', function(evt) {
  chrome.runtime.sendMessage({ type: 'open', data: evt.detail}); // <- attacker-controlled via custom event
});

// Background script (bg.js Line 1004-1014)
chrome.runtime.onMessage.addListener(request => {
    if (request.type === "open") {
        setTimeout(()=>{
          createPopup(request) // <- passes attacker data to createPopup
        }, "1500");
    }
})

// Background script (bg.js Line 965-968)
function createPopup(request){
  chrome.storage.sync.set({ request: request.data }).then(() => { // <- storage poisoning
    // console.log("Value is set to " + JSON.stringify(request.data));
  });
  // ... creates popup window
}

// Popup page retrieval (pages/popupResult.js Line 26-34)
async function getRequest() {
    let data = "";
    await chrome.storage.sync.get(["request"]).then((result) => {
        data = result; // <- reads poisoned storage
    });
    return data;
}

// Data sent to hardcoded backend (pages/popupResult.js Line 41-51)
async function decodeData(address, dataInput, sourceUrl) {
    const data = { address: address, dataInput: dataInput , sourceUrl:sourceUrl};
    try {
        let res = await fetch("https://api.truston.app/api/data-decode-v2/", { // <- hardcoded backend
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        });
        // ...
    }
}
```

**Classification:** FALSE POSITIVE

**Reason:** While an attacker can poison chrome.storage.sync via a custom DOM event, the stored data is only retrieved and sent to the developer's hardcoded backend URL (https://api.truston.app/api/data-decode-v2/). According to the threat model, hardcoded backend URLs are trusted infrastructure. The attacker cannot retrieve the poisoned data back or use it in any exploitable operation. This is an incomplete storage exploitation chain without attacker-accessible output.
