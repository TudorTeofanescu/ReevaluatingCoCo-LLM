# CoCo Analysis: gcgoenndigjegpgpfnnmgfnbiollgimk

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3 (same vulnerability, different tainted parameters)

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_tabs_executeScript_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gcgoenndigjegpgpfnnmgfnbiollgimk/opgen_generated_files/bg.js
Line 965 - Multiple tainted flows from external message (a.service, a.time, a.id)

**Code:**

```javascript
// Background script - External message handler with code execution (bg.js Line 965)
chrome.runtime.onMessageExternal.addListener(function(a, b) {
    if (a.URL) { // ← attacker-controlled message
        var c = a.service, // ← attacker-controlled
            d = a.time,    // ← attacker-controlled
            e = a.URL,     // ← attacker-controlled
            f = b.tab,
            g = function(a) {
                var b = a[0],
                    c = a[1],
                    d = a[2],
                    e = a[3],
                    f = "("+function(a){{var b=a[0];a[1],a[2]}y=$(\".player\").scope(),x=y.player,x.volume=0,x.playerStarted||x.playing||(x.volume=0,$(\".cloudcast-play\").click());var c=setInterval(function(){x.volume=0,x.playerStarted&&x.playing&&!y.webPlayer.loading&&(y.$apply(function(){y.$emit(\"slider:stop\",b/1e3),x.volume=1}),clearInterval(c))},100)}+\")("+JSON.stringify([c,d,e])+")\"",
                    g = "("+function(a){var b=a[0],c=(a[1],a[2],setInterval(function(){window.frames[1]&&window.frames[1].require&&window.frames[1].require([\"$api/models\"],function(a){player=a.player,a.player.load(\"track\").done(function(){if(player.track&&player.track.number&&player.track.album&&(player.track.uri.contains(\"spotify:track\")||player.track.uri.contains(\"spotify:album\"))){clearInterval(c),_album=player.track.album,_number=player.track.number,player.stop(),player.playContext(_album,_number-1,b);var a=function(){player.stop(),player.playContext(_album,_number,0)},d=function(){player.removeEventListener(\"change:track\",a)};player.addEventListener(\"change:track\",a),player.addEventListener(\"change:track\",d)}})})},500))}+\")("+JSON.stringify([c,d,e])+")\"",
                    h = document.createElement("script");
                "mixcloud" == b && (h.textContent = f);
                "spotify" == b && (h.textContent = g);
                "another" == b && (h.textContent = "another");
                (document.head || document.documentElement).appendChild(h);
                h.parentNode.removeChild(h)
            };

        // Attacker-controlled data flows into executeScript
        chrome.tabs.create({url: e}, function(a) {
            chrome.tabs.executeScript(null, {
                code: "(" + g + ")(" + JSON.stringify([c, d, a.id, f.id]) + ");" // ← attacker-controlled data in executed code
            });
        });
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onMessageExternal - External message from whitelisted domains

**Attack:**

```javascript
// Malicious script on any whitelisted domain (*.stereopaw.com, *.soundcloud.com,
// *.youtube.com, *.mixcloud.com, *.spotify.com) can send external message
chrome.runtime.sendMessage('gcgoenndigjegpgpfnnmgfnbiollgimk', {
    URL: 'https://www.mixcloud.com/',
    service: 'mixcloud',
    time: 1000
});

// The extension will:
// 1. Create a new tab with the URL
// 2. Execute code that includes attacker-controlled 'service' and 'time' parameters
// 3. While the main code structure is hardcoded, the attacker controls:
//    - The URL of the created tab
//    - Values that get JSON.stringify'd into the executed code
//    - The 'service' parameter that determines which code path executes

// More severe exploit - if attacker finds injection point:
// The JSON.stringify includes attacker values, potentially allowing code injection
// depending on how the serialized data is used in the executed context
```

**Impact:** Arbitrary code execution vulnerability. External messages from whitelisted domains (which includes major music platforms) can trigger creation of new tabs and execution of code with attacker-controlled parameters. While the main code structure is hardcoded, attacker-controlled values (service, time, tab IDs) are serialized into the executeScript payload. The extension has tabs and activeTab permissions. This allows any website on the whitelisted domains (or any extension, per manifest v2 behavior) to execute code in newly created tabs with some attacker control over the parameters.

