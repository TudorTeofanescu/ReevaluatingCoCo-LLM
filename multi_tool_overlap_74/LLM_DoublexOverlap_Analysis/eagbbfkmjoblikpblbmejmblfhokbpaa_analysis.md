# CoCo Analysis: eagbbfkmjoblikpblbmejmblfhokbpaa

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_downloads_download_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/eagbbfkmjoblikpblbmejmblfhokbpaa/opgen_generated_files/bg.js
Line 982    chrome.downloads.download({ url: request.url })
```

**Code:**

```javascript
// Background script - External message listener (bg.js line 980)
chrome.runtime.onMessageExternal.addListener((request, sender, sendResponse) => {
    if (request.contentScriptQuery == "downloadUrl") {
        chrome.downloads.download({ url: request.url })
    }
    return true
})
```

**Classification:** FALSE POSITIVE

**Reason:** The extension uses "externally_connectable" in manifest.json with a whitelist restricting external messages to only "*.mover.uz/*" domains. The extension is designed to download videos from mover.uz, and only pages/extensions from that domain can trigger the download functionality. This is not exploitable by arbitrary external attackers since they cannot send messages to this extension without being on the whitelisted domain.
