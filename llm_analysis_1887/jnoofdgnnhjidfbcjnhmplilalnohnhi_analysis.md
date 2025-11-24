# CoCo Analysis: jnoofdgnnhjidfbcjnhmplilalnohnhi

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: document_eventListener_store_request → chrome_storage_sync_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jnoofdgnnhjidfbcjnhmplilalnohnhi/opgen_generated_files/cs_1.js
Line 585     document.addEventListener(id, function (event) {
Line 587         callback(event.detail)
Line 631     chrome.storage.sync.get(request.data, function (result) {
```

**Code:**

```javascript
// Content script - UIMessages library (lines 584-591 in cs_1.js)
listen: function (id, callback) {
    document.addEventListener(id, function (event) {
        if (callback) {
            callback(event.detail)  // ← event.detail passed to callback
        }
    });
}

// Content script - Storage request handler (lines 629-647 in cs_1.js)
UIMessages.listen("store_request", function (request) {
    if (request.method == "get") {
        chrome.storage.sync.get(request.data, function (result) {
            UIMessages.send("store_response", {
                method: "get",
                data: result
            });
        });
    }
    if (request.method == "set") {
        chrome.storage.sync.set(request.data, function () {  // ← storage write
            UIMessages.send("store_response", {
                method: "set",
                data: request.data,
                status: "OK"
            });
        });
    }
});

// Injected script (is-dice.js) - Only legitimate extension code can trigger
function updateValue(name, newValue) {
    if (newValue != CONTROL[name]) {
        console.log("Value of " + name + " changed to: " + newValue);
        CONTROL[name] = newValue;
        var data = {};
        data[name] = newValue;
        UIMessages.send("store_request", {
            method: "set",
            data: data  // ← Extension's own UI values
        });
    }
}
```

**Classification:** FALSE POSITIVE

**Reason:** The event listener is for custom events dispatched by the extension's own injected script (is-dice.js), not by external attacker-controlled webpages. The injected script (is-dice.js) is executed in the page context and dispatches custom events to communicate with the content script. While this creates a communication channel, the event names are specific ("store_request", "store_response", "license_request", etc.) and the data flow is from the extension's own UI to storage - storing user preferences from the extension's dice gambling automation interface. The extension only runs on specific yobit.io/yobit.net/yobitex.net domains (per manifest content_scripts matches), and the storage operations save legitimate extension settings (strategy, attempts, interval, multiplier, etc.). An attacker on the yobit website could theoretically dispatch matching events, but this only allows poisoning extension settings (like gambling strategy preferences), which does not achieve exploitable impact since the stored data is only used internally by the extension's own UI and doesn't flow back to the attacker or trigger privileged operations.
