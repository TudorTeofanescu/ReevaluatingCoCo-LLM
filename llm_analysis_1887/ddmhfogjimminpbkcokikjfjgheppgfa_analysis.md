# CoCo Analysis: ddmhfogjimminpbkcokikjfjgheppgfa

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 4 (variations of same flow)

---

## Sink: document_eventListener_muralUserData → chrome_storage_sync_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ddmhfogjimminpbkcokikjfjgheppgfa/opgen_generated_files/cs_0.js
Line 571	function onMuralUserData(e) {
Line 573	    muralUserData = e.detail;
Line 576	    if(muralUserData.name) {
```

**Code:**

```javascript
// Content script (cs_0.js)

// Function that sets up the event listener and triggers data collection
function refreshMuralUserData() {
    if(refreshMuralUserDataTimeout) {
        clearTimeout(refreshMuralUserDataTimeout);
    }

    document.addEventListener('muralUserData', onMuralUserData);

    // Extension injects its OWN script to dispatch the event
    const refreshMuralUserDataScript = `
    setTimeout(function() {
        document.dispatchEvent(new CustomEvent('muralUserData', {
            detail: { name: app.me.fullName, color: app.me.color } // ← Data from MURAL app
        }));
    }, 0);`;
    injectMuralScript(refreshMuralUserDataScript); // Injects into page context
}

// Event handler that receives the data
function onMuralUserData(e) {
    document.removeEventListener('muralUserData', onMuralUserData);
    muralUserData = e.detail; // Data from MURAL's app object

    let hasName = false;
    if(muralUserData.name) {
        hasName = true;
    } else {
        muralUserDataInitialized = false;
    }

    if(hasName) {
        if(!muralUserDataInitialized) {
            // save muralUserData in storage
            getStoredData(function(data) {
                data.storedData.muralUserData = muralUserData;
                saveStoredData(data.storedData, function() { // Calls chrome.storage.sync.set
                    muralUserDataInitialized = true;
                });
            });
        }
    } else {
        refreshMuralUserDataTimeout = setTimeout(refreshMuralUserData, 1000);
    }
}

// Helper function that injects script into page
function injectMuralScript(script) {
    const scriptTag = document.createElement("script");
    document.head.appendChild(scriptTag);
    scriptTag.innerHTML = script;
    document.head.removeChild(scriptTag);
    scriptTag.innerHTML = null;
}
```

**Classification:** FALSE POSITIVE

**Reason:** No external attacker trigger. The document.addEventListener('muralUserData') only receives events that the extension itself dispatches. The flow is: (1) Extension calls refreshMuralUserData(), (2) Extension injects its own script via injectMuralScript() that accesses MURAL's internal app.me object, (3) That injected script dispatches a CustomEvent with data from app.me.fullName and app.me.color, (4) Extension's own event listener receives this event and stores the data. An external attacker cannot dispatch this event because: the event is triggered by the extension's own injected script, the data comes from MURAL's internal application object (app.me), not from attacker input, and there's no pathway for an attacker to inject arbitrary data into this flow. This is internal extension logic, not an externally exploitable vulnerability. The extension is simply reading user data from the MURAL application and storing it for its own use.
