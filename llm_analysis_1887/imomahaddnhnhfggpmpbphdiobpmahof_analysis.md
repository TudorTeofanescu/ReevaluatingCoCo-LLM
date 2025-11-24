# CoCo Analysis: imomahaddnhnhfggpmpbphdiobpmahof

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/imomahaddnhnhfggpmpbphdiobpmahof/opgen_generated_files/bg.js
Line 996 `preloadImgs(request.files);`
Line 976 `imgs = JSON.parse(imgs);`
Line 978 `if (imgs[key].indexOf('themes_pic_file') > 0) {`
Line 979 `img_files.push('https://youtube-skins.com' + imgs[key]);`

**Code:**

```javascript
// Background script - External message listener (line 988-1002)
chrome.runtime.onMessageExternal.addListener(
    function (request, sender, sendResponse) {
        if (request.action == 'install') {
            chrome.storage.local.get('skins').then(function (e) {
                delete request.action;
                skins = [];
                if (e.skins !== undefined)
                    skins = e.skins;
                preloadImgs(request.files); // ← attacker-controlled from *.youtube-skins.com
                skins.unshift(request);
                chrome.storage.local.set({
                    skins: skins
                });
            });
        }
    }
);

// preloadImgs function (lines 975-986)
function preloadImgs(imgs) {
    imgs = JSON.parse(imgs); // ← attacker-controlled JSON
    for (var key in imgs) {
        if (imgs[key].indexOf('themes_pic_file') > 0) {
            // URL construction: hardcoded domain + attacker-controlled path
            img_files.push('https://youtube-skins.com' + imgs[key]); // ← attacker controls path portion
        }
    }
    if (img_files.length > 0) {
        httpPreload(img_files.shift()); // Fetches the constructed URL
    }
}
```

**Classification:** FALSE POSITIVE

**Reason:** While external messages from *.youtube-skins.com can control the `imgs[key]` value that gets concatenated to the URL, the final fetch destination is constrained to the hardcoded domain 'https://youtube-skins.com' (the developer's own infrastructure). The attacker can only control the path portion of the URL (e.g., '/themes_pic_file/path'), not the destination domain. According to the methodology, "Data TO hardcoded backend: `fetch("https://api.myextension.com", {body: attackerData})`" and requests going to developer's own infrastructure are considered trusted infrastructure. The youtube-skins.com domain is the same domain whitelisted in externally_connectable, indicating it's owned by the extension developer. This is effectively sending attacker-controlled paths to the developer's own backend, which is not an exploitable vulnerability under the threat model.
