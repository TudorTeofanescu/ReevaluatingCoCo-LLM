# CoCo Analysis: nbaalnodnkcjgbpfkphhndpbjnnglnni

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nbaalnodnkcjgbpfkphhndpbjnnglnni/opgen_generated_files/bg.js
Line 965   (minified webpack bundle containing the handler)

**Code:**

```javascript
// Background script (bg.js) - Line 965 (minified, formatted for clarity)
chrome.runtime.onMessageExternal.addListener((function(e, t, r) {
    switch(e.type) {
        case "datalink":
            var o = e.data;  // Attacker-controlled input
            if(o) {
                var a = o.split("\n").filter(e => "" !== e.trim());
                if(a.length > 1) {
                    let e = n();  // Generate internal job_id
                    chrome.storage.local.set({
                        csvhead: ["登録","決済","追跡番号"].concat(a[0].split(",")),  // Attacker-controlled
                        csvbody: a.filter((e,t) => t>0).map(e => ["","",""].concat(e.split(","))),  // Attacker-controlled
                        job_id: e  // Internal job_id
                    }, () => {
                        r({rows: a.length-1, job_id: e})  // sendResponse with internal job_id only
                    })
                } else {
                    r({rows: 0})
                }
            } else {
                r({rows: 0})
            }
    }
    return true;
}))
```

**Classification:** FALSE POSITIVE

**Reason:** Storage poisoning without retrieval path for poisoned data. While external entities can write attacker-controlled CSV data to storage via the "datalink" message type, the sendResponse callback only returns the internally-generated job_id and row count, not the poisoned data itself. There is no mechanism for the attacker to retrieve the malicious data they stored (no subsequent operation that sends the stored csvhead/csvbody back to the attacker).
