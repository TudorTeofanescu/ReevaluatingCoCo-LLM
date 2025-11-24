# CoCo Analysis: fadmekhncmoghkkpfohhflefbmcgekfo

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** Multiple (all variants of XMLHttpRequest_responseText_source → JQ_obj_html_sink)

---

## Sink: XMLHttpRequest_responseText_source → JQ_obj_html_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/fadmekhncmoghkkpfohhflefbmcgekfo/opgen_generated_files/bg.js
Line 332: `XMLHttpRequest.prototype.responseText = 'sensitive_responseText';`
Line 972: `var data = JSON.parse(xhr.responseText);`
Line 973: `if(data["stream"] === null){`
Line 981: `var stream_game = data["stream"].game;`
Line 985: `$("#game").html('Jeu en cours de stream: ' + stream_game);`

**Code:**

```javascript
// Background script - Extension's own popup UI
var tickRate = 5000;

function checkStream(){
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "https://api.twitch.tv/kraken/streams/htmosa?client_id=7dqgft8dbkye31ixffpnzyxmbrus8c", true); // ← hardcoded backend
  xhr.onreadystatechange = function(){
    if(xhr.readyState == 4){
      var data = JSON.parse(xhr.responseText);
      if(data["stream"] === null){
        $("#info").css("color","red");
        $("#info").html("Htmosa n'est pas en live actuellement :(");
        $('#game').hide();
        $('#viewers').hide();
        chrome.browserAction.setIcon({path: "img/off.png"});
        chrome.browserAction.setBadgeText({text: "Off"});
      }else{
        var stream_game = data["stream"].game; // Data from Twitch API
        var stream_viewers = data["stream"].viewers;
        $("#info").css("color","green");
        $("#info").html("Htmosa est en live actuellement :)");
        $("#game").html('Jeu en cours de stream: ' + stream_game); // jQuery .html() sink in popup
        $("#viewers").html('Nombres de viewers: ' + stream_viewers);
        chrome.browserAction.setIcon({path: "img/on.png"});
        chrome.browserAction.setBadgeText({text: "On"});
      }
      setTimeout(checkStream, tickRate)
    }
  }
  xhr.send();
}

checkStream();
setInterval(checkStream, tickRate);
```

**Classification:** FALSE POSITIVE

**Reason:** Data flows from hardcoded backend URL (Twitch API: https://api.twitch.tv/kraken/streams/htmosa) to jQuery .html() sink in the extension's own popup page. This is the extension's trusted backend infrastructure. The sink (jQuery .html()) only affects the extension's own popup UI, not any web page content. No external attacker can trigger this flow or control the Twitch API response. Compromising Twitch's API infrastructure is separate from extension vulnerabilities. While .html() could lead to XSS in the popup context, the source is a hardcoded trusted backend, making this a FALSE POSITIVE under the methodology's "Hardcoded Backend URLs" rule.
