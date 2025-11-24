# CoCo Analysis: blbckhiepgpniilpmlionnkjoeehhgao

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 10 (5 unique detection timestamps, each reported twice)

---

## Sink 1-10: fetch_source → chrome_downloads_download_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/blbckhiepgpniilpmlionnkjoeehhgao/opgen_generated_files/bg.js
- Source: fetch_source (Line 265 - mock data: `var responseText = 'data_from_fetch'`)
- Flow: Line 265 → Line 1002 → window.URL.createObjectURL(blob) → chrome.downloads.download()
- Sink: chrome.downloads.download with URL from fetch response

**Code:**

```javascript
// Background script - background.js
function downloadVideo(a, b) {
    var c, e, d;
    return $jscomp.asyncExecutePromiseGeneratorProgram(function(f) {
        if(1 == f.nextAddress)
            return a.downloadUrl.startsWith("blob") ?
                f.yield(download(a.downloadUrl, a.authorId, a.videoId, b), 3) :
                (a.downloadUrl.includes("tiktokcdn.com") ? (
                    c = null,
                    fetch(a.downloadUrl) // ← Fetch from tiktokcdn.com
                        .then(function(a) {
                            if(!a.ok) throw Error("Network response was not ok");
                            return a.blob() // ← Blob from fetch
                        })
                        .then(function(b) {
                            if(c = window.URL.createObjectURL(b)) // ← Create blob URL
                                b = download(c, a.authorId, a.videoId, "DOWNLOAD"), // ← Download
                                onDownloadComplete(b) && recordDownload("tt")
                        })
                        .catch(function(a) {
                            hideLoadingOnDownloadButton(downloadButton)
                        })
                ) : // ... alternative flow
                chrome.tabs.query({active:!0, currentWindow:!0}, function(c) {
                    chrome.tabs.sendMessage(c[0].id, {downloadUrl: a.downloadUrl}, function(c) {
                        downloadVideoV2(c.downloadUrl, a.authorId, a.videoId, b)
                    })
                }),
                f.jumpTo(0)
            );
    })
}

// Message listener that triggers download
chrome.runtime.onMessage.addListener(function(a, b, c) {
    "DOWNLOAD" == a.type ? (
        downloadVideo(a, a.type), // ← Called with message data
        c()
    ) : "TTMDOWNLOAD" == a.type && (
        downloadAllVideos(a.downloadUrl, a.type),
        c()
    )
});
```

**Classification:** FALSE POSITIVE

**Reason:** While the flow exists (fetch → blob → download), this is NOT an attacker-exploitable vulnerability:

1. **Hardcoded URL Domain:** The fetch() is called ONLY when `a.downloadUrl.includes("tiktokcdn.com")` - downloads are restricted to TikTok's CDN domain
2. **Intended Functionality:** This is a TikTok video downloader extension - downloading from tiktokcdn.com is its legitimate purpose
3. **Not Arbitrary Downloads:** The URL must:
   - Be provided via chrome.runtime.onMessage (from content script, not external)
   - Include "tiktokcdn.com" in the URL
   - Content script only runs on `*://*.tiktok.com/*` per manifest

4. **Content Script Message Source:** The message comes from content scripts running on tiktok.com, triggered by user action (clicking download button), not from arbitrary websites

5. **User-Initiated Action:** Per manifest and code structure:
   - Extension has page_action (popup) on TikTok pages
   - User must click download button in extension popup
   - Content script extracts video URL from TikTok page
   - Sends message to background with video URL
   - This is user-initiated download of TikTok videos, not attacker-controlled

6. **No External Attacker Trigger:**
   - No chrome.runtime.onMessageExternal (no external messages accepted)
   - No window.postMessage listeners that could be exploited
   - Content script only on tiktok.com, and messages are internal

**CoCo Detection Analysis:**
CoCo detected the taint flow: fetch_source → blob → download, which is technically correct data flow. However, the SOURCE is not attacker-controlled:
- The downloadUrl comes from user interaction with TikTok pages
- It's validated to be from tiktokcdn.com
- This is the extension's intended functionality, not a vulnerability

**Conclusion:** This is a FALSE POSITIVE because:
1. No external attacker trigger exists (per methodology: "Can attacker trigger the flow?")
2. Downloads are restricted to hardcoded trusted domain (tiktokcdn.com)
3. This is intended functionality - TikTok video downloader downloading from TikTok CDN
4. User-initiated action in extension popup, not attacker-controlled flow
