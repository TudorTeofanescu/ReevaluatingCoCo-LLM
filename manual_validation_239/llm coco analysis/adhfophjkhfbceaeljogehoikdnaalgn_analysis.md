# CoCo Analysis: adhfophjkhfbceaeljogehoikdnaalgn

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2 (both same vulnerability pattern)

---

## Sink 1-2: document_eventListener_ChromeInfomaxEvent → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/adhfophjkhfbceaeljogehoikdnaalgn/opgen_generated_files/cs_0.js
Line 470: `function(e) {`
Line 481: `if (e.detail && e.detail.type === 'save') {`

Both detections reference the same DOM event listener that writes to storage.

**Code:**

```javascript
// Content script - DOM event listener (cs_0.js, lines 468-487)
document.addEventListener(
    'ChromeInfomaxEvent',
    function(e) {  // ← attacker-controlled event
        if (e.detail && e.detail.type === 'save') {
            chrome.storage.sync.set({ urlCtrl: e.detail }, function() {});  // Storage write
        }
    },
    false
);

// Background script - Storage retrieval (bg.js, lines 1015-1053)
chrome.storage.sync.get(['userkey', 'urlExcludeList', 'urlCtrl'], function(data) {
    if (data && data.userkey) {
        let isRun = false;

        const { viewOption, allowUrls, denyUrls } = data.urlCtrl;  // ← reads poisoned data

        if (viewOption === '보지 않기') {
            // Don't show
        } else if (viewOption === '선택된 사이트만 보기') {
            if (allowUrls.find((str) => realUrl.includes(str))) {  // ← uses poisoned allowUrls
                isRun = true;
            }
        } else if (viewOption === '모든 사이트 보기') {
            if (!denyUrls.find((str) => realUrl.includes(str))) {  // ← uses poisoned denyUrls
                isRun = true;
            }
        }

        if (isRun) {
            const code = `
                (function(){
                    if(!document.getElementById("infomax_ifrm_super")){
                        var iframe = document.createElement('iframe');
                        iframe.setAttribute('id', 'infomax_ifrm_super');
                        iframe.src = 'https://chrome.einfomax.co.kr/view/${data.userkey}'  // Hardcoded URL
                        iframe.scrolling = 'no'
                        iframe.frameBorder = 0
                        iframe.style.cssText = 'position: fixed;bottom: 0px;left: 0px;width: 100%;height: 30px;...'
                        document.documentElement.appendChild(iframe)
                    }
                })()
            `;
            chrome.tabs.executeScript(id, { code });  // Executes hardcoded code only
        }
    }
});
```

**Classification:** FALSE POSITIVE

**Reason:** While this has a complete storage exploitation chain (attacker writes to storage → extension reads from storage → uses data), it lacks exploitable impact. The attacker-controlled data (`viewOption`, `allowUrls`, `denyUrls`) only controls WHEN/WHERE the extension injects an iframe, not WHAT is injected. The actual code executed is hardcoded (lines 1035-1049) and injects a fixed iframe to `https://chrome.einfomax.co.kr/view/${data.userkey}`. The attacker cannot:
- Execute arbitrary code (code is hardcoded)
- Make privileged requests to attacker-controlled URLs (URL is hardcoded)
- Download arbitrary files
- Exfiltrate sensitive data back to themselves
- Retrieve the poisoned data via sendResponse/postMessage

The poisoned data is used only for internal access control logic (which sites trigger the iframe), which doesn't meet the "Exploitable Impact" criteria in the methodology.
