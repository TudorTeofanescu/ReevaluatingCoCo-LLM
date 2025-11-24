# CoCo Analysis: iedifognpinkpfaemlnnniomklocpcnh

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 3

---

## Sink 1: bg_chrome_runtime_MessageExternal → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/iedifognpinkpfaemlnnniomklocpcnh/opgen_generated_files/bg.js
Line 965: Shows chrome.runtime.onMessageExternal.addListener receiving `t.payload` which flows to URLs constructed for fetch:
- `t.media_id` → used in URL construction
- `t.min_id` → used in URL parameter construction

**Analysis:**

The extension is "AppSorteos" - an Instagram giveaway tool. It listens for external messages and constructs URLs to fetch data from Instagram's API:

**Code:**

```javascript
// Background script (line 965) - minified and condensed
chrome.runtime.onMessageExternal.addListener(async(t,e,n)=>{
    var i,o,r=t.payload; // ← External message payload (attacker-controlled)

    // ... status and info handlers ...

    if(t&&"comments"===t.type){
        t=r;
        var a=n;
        // Constructs URL with attacker-controlled data
        let e="https://www.instagram.com/api/v1/media/"+t.media_id+"/comments/?can_support_threading=true&permalink_enabled=false";
        t.min_id&&(e+="&min_id="+encodeURIComponent(t.min_id)); // ← t.min_id from attacker

        // Fetch to constructed URL (hardcoded Instagram domain)
        fetch(e,{method:"GET",headers:s()}).then(e=>e.json()).then(e=>{
            console.log(e),a&&a(e)
        }).catch(e=>{a({error:!0})})
    }
})
```

**Manifest permissions:**
```json
"externally_connectable": {
    "matches": ["https://*.app-sorteos.com/*"]
},
"host_permissions": ["*://*.instagram.com/*"]
```

**Classification:** FALSE POSITIVE

**Reason:** While attacker-controlled data flows into the fetch URL, the base URL is hardcoded to Instagram's API (`https://www.instagram.com/api/v1/media/`). The attacker can only control the `media_id` and `min_id` parameters which are used in a legitimate API call to Instagram. This allows the attacker to:
1. Query Instagram comments for arbitrary media IDs (but this is public Instagram data)
2. The response is returned to the attacker via callback

This is not a true SSRF vulnerability because:
- The destination is hardcoded to Instagram's public API (not attacker-controlled arbitrary URLs)
- The attacker cannot reach internal networks or arbitrary external hosts
- The functionality is the intended behavior of the extension (fetching Instagram data on behalf of whitelisted websites)

While there's a privacy concern (whitelisted sites can query Instagram data), this is the extension's designed functionality, not a security vulnerability under the threat model. The attacker cannot perform privileged cross-origin requests to arbitrary destinations.

---

## Sink 2: bg_chrome_runtime_MessageExternal → fetch_resource_sink (duplicate)

Same as Sink 1, just detected twice by CoCo with different trace paths.

---

## Sink 3: fetch_source → sendResponseExternal_sink

**CoCo Trace:**
Line 265: `var responseText = 'data_from_fetch';` (framework mock code)

**Analysis:**

This detection is in the CoCo framework mock code (Line 265 is before line 963 where actual extension code starts). The actual extension does fetch Instagram data and return it via callbacks to external callers, but this is the extension's intended functionality - acting as a proxy to fetch Instagram public data for whitelisted domains.

**Classification:** FALSE POSITIVE

**Reason:** CoCo detected this in framework mock code. The actual behavior (fetching Instagram public API data and returning to caller) is the extension's designed functionality for whitelisted domains, not a vulnerability.
