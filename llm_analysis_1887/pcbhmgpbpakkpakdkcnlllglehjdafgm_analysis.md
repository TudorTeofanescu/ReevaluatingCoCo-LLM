# CoCo Analysis: pcbhmgpbpakkpakdkcnlllglehjdafgm

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 4 (all chrome.tabs.executeScript with message parameter)

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_tabs_executeScript_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pcbhmgpbpakkpakdkcnlllglehjdafgm/opgen_generated_files/bg.js
Line 1026 chrome.tabs.executeScript(tab.id, {"file": "js/"+message+".js"});

**Code:**

```javascript
// bg.js (background script)
chrome.extension.onMessageExternal.addListener(function(message, sender, sendResponse) {
	if(message=='next' || message=='prev') {  // ← strict validation
		chrome.tabs.query({}, function(tabs) {
			var res = false;
			for (var i = 0, tab; tab = tabs[i]; i++) {
				if (tab.url.indexOf(playerUrl)>=0) {
					chrome.tabs.executeScript(tab.id, {"file": "js/"+message+".js"}); // ← only "js/next.js" or "js/prev.js"
					res = true;
					_gaq.push(['_trackEvent', message, 'clicked']);
					break;
				}
			}
			if (!res) {
				chrome.tabs.create({"url" : playerUrl},execScriptOnTab);
				_gaq.push(['_trackEvent', "tab", 'opened']);
			}
		});
	}
});

// js/next.js (hardcoded script)
var button = $('.player-controls__btn_next');
button.attr('id', 'nextButton');
nextButton = document.getElementById('nextButton');
var _event = document.createEvent("MouseEvents");
_event.initMouseEvent("click",true,true,this,0,0,0,0,0,false,false,false,false,0, null);
nextButton.dispatchEvent(_event);

// js/prev.js (hardcoded script)
var button = $('.b-jambox__prev');
button.attr('id', 'nextButton');
nextButton = document.getElementById('nextButton');
var _event = document.createEvent("MouseEvents");
_event.initMouseEvent("click",true,true,this,0,0,0,0,0,false,false,false,false,0, null);
nextButton.dispatchEvent(_event);
```

**Classification:** FALSE POSITIVE

**Reason:** While chrome.extension.onMessageExternal allows external messages, the message parameter is strictly validated with `if(message=='next' || message=='prev')` before being used. The attacker can only execute two hardcoded, benign scripts (js/next.js or js/prev.js) which simply simulate clicking next/prev buttons on Yandex Music player. No arbitrary code execution is possible.
