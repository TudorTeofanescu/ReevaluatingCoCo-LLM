# CoCo Analysis: nebafhfaccmdnfokjcpknfommfdflkac

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2 (same flow, two storage keys)

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nebafhfaccmdnfokjcpknfommfdflkac/opgen_generated_files/cs_0.js
Line 2394 (function receiveMessage)
Line 2396 (evt.data)
Line 2399 (data.clientid)
Line 2400 (data.clientsecret)

**Code:**

```javascript
// Content script - window message listener
window.addEventListener('message', receiveMessage, false);

function receiveMessage(evt) {
    if (evt.origin === "https://datto.amp.vg" || evt.origin === "https://borderstates.amp.vg" || evt.origin === "https://dhalia.amp.vg") {
        var data = $.parseJSON(evt.data);

        install = $("#ampserverurl").val(); // From DOM element, not attacker
        clientId = data.clientid; // ← attacker-controlled
        clientSecret = data.clientsecret; // ← attacker-controlled

        chrome.storage.local.set({ 'install': install });
        chrome.storage.local.set({ 'clientid': clientId }); // Storage write
        chrome.storage.local.set({ 'clientsecret': clientSecret }); // Storage write

        // ... later retrieval:
        chrome.storage.local.get(['install', 'clientid', 'clientsecret'], function (result) {
            install = result.install;
            clientid = result.clientid;
            clientSecret = result.clientsecret;

            // Used in apiHelper which sends to hardcoded backend:
            apiHelper.call("GetAllConnectedSocialSites", { userid: permissionsJo.userid }, ...);
        });
    }
}

// apiHelper sends data to hardcoded backend:
var apiHelper = {
    call: function (api, data, callback, headers) {
        var apiUrl = install + "/api/" + api + "?token=" + clientSecret; // install from DOM, not attacker
        $.ajax({
            type: "POST",
            url: apiUrl, // Goes to trusted backend
            data: apiData
        })
    }
}
```

**Classification:** FALSE POSITIVE

**Reason:** Data flows to hardcoded backend (trusted infrastructure). While the attacker can poison storage with clientid/clientsecret from whitelisted origins, the stored credentials are sent to the `install` URL which comes from the DOM element `$("#ampserverurl").val()`, not from the attacker's message. The data goes TO the developer's backend, not back to the attacker.
