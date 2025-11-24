# CoCo Analysis: appokpamleklabmcabcglklabhadlbmd

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 3 (all same flow, different trace variations)

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/appokpamleklabmcabcglklabhadlbmd/opgen_generated_files/cs_0.js
Line 477	window.addEventListener('message', (event) => {
Line 479	    const data = event.data;
Line 491	                chrome.storage.session.get(data.raid_id).then(r=>{
Line 497	                    r = r[data.raid_id];
Line 500	                        t = t[r];
Line 508	                        t[data.raid_id] = loot;
```

**Code:**

```javascript
// Content script - postMessage listener (cs_0.js line 477-520)
window.addEventListener('message', (event) => {
    if (event.source !== window) return;
    const data = event.data; // ← attacker-controlled from webpage

    if (data.command) {
        switch (data.command) {
            case "ADD_PENDING":
                chrome.storage.session.set({[data.raid_id]: data.quest_id}); // Storage write
                break;
            case "RESOLVE_PENDING":
                chrome.storage.session.get(data.raid_id).then(r=>{ // ← attacker-controlled key
                    if (Object.keys(r).length === 0) {
                        return;
                    }
                    r = r[data.raid_id];
                    chrome.storage.session.remove(data.raid_id);
                    chrome.storage.local.get({[r]: {}}).then(t=>{
                        t = t[r];
                        const loot = {};
                        for (key in data.loot) { // ← attacker-controlled data
                            if (Object.keys(data.loot[key]).length > 0) {
                                loot[key] = Object.values(data.loot[key]).map(itemMap);
                            }
                        }
                        t[data.raid_id] = loot; // ← attacker-controlled key and value
                        chrome.storage.local.set({[r]: t}); // Storage write sink
                    });
                });
            break;
        }
    }
});
```

**Classification:** FALSE POSITIVE

**Reason:** This is incomplete storage exploitation. The attacker can poison chrome.storage via postMessage (attacker-controlled data flows to storage.set), but there is no retrieval path where the stored data flows back to the attacker via sendResponse, postMessage, or is used in a subsequent vulnerable operation (fetch to attacker URL, executeScript, etc.). Storage poisoning alone without a retrieval mechanism is not exploitable per the methodology.
