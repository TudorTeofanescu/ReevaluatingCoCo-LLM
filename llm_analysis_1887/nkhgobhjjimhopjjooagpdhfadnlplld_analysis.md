# CoCo Analysis: nkhgobhjjimhopjjooagpdhfadnlplld

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 9 (multiple variations of same flow)

---

## Sink: cs_window_eventListener_SendLoadout -> fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nkhgobhjjimhopjjooagpdhfadnlplld/opgen_generated_files/cs_0.js
Line 470: `window.addEventListener("SendLoadout", function(evt) {`
Line 471: `chrome.runtime.sendMessage(evt.detail, on_loadout_sent);`

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nkhgobhjjimhopjjooagpdhfadnlplld/opgen_generated_files/bg.js
Line 984: `message.data.API = apiKey;`
Line 1053: `const url = serverAddress + \`/get_loadout.php?uid=${data.uid}&api=${data.API}\`;`

**Code:**

```javascript
// Content script (contentscript.js) - Entry point
window.addEventListener("SendLoadout", function(evt) {
    chrome.runtime.sendMessage(evt.detail, on_loadout_sent); // <- attacker-controlled evt.detail
}, false);

// Background script (background.js)
let serverAddress = "https://tornloadout.xyz/"; // <- hardcoded backend URL

chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
    message.data.API = apiKey;

    if (message.type == "get_loadout") {
        get_loadout(message.data, sendResponse);
    }
    return true;
});

function get_loadout(data, sendResponse) {
    // URL constructed with attacker-controlled data.uid
    const url = serverAddress + `/get_loadout.php?uid=${data.uid}&api=${data.API}`; // <- data.uid from attacker

    fetch(url, { // <- fetch to hardcoded backend
        method: 'GET',
    })
    .then(response => response.json())
    .then(data => {
        sendResponse(data);
    });
}
```

**Classification:** FALSE POSITIVE

**Reason:** Although attacker-controlled data (evt.detail.data.uid) flows into the fetch URL, the base URL is hardcoded to "https://tornloadout.xyz/" which is the developer's backend infrastructure. The attacker can only control query parameters sent to the developer's trusted backend, not the destination of the fetch request itself. This is trusted infrastructure, not a vulnerability.

---

## Sink: cs_window_eventListener_SendAttackLogs -> fetch_resource_sink

Same pattern as SendLoadout - attacker controls message parameters that are sent to the hardcoded backend URL. All 9 detected sinks follow the same pattern with variations in which field (data.uid, message.api, etc.) flows to the hardcoded backend URL.

**Classification:** FALSE POSITIVE (same reason - trusted infrastructure)
