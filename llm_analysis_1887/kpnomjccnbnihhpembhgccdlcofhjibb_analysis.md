# CoCo Analysis: kpnomjccnbnihhpembhgccdlcofhjibb

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2 (duplicate detections of same flow)

---

## Sink: XMLHttpRequest_responseText_source → XMLHttpRequest_url_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kpnomjccnbnihhpembhgccdlcofhjibb/opgen_generated_files/bg.js
Line 332: XMLHttpRequest.prototype.responseText = 'sensitive_responseText';
Line 987: var data = JSON.parse(xhr.responseText);
Line 989: if(data["data"][0] == null){
Line 998: xhrjeu.open("GET", "https://api.twitch.tv/helix/games?id=" + data["data"][0]["game_id"], true);

**Code:**

```javascript
// Background script - Internal extension logic only
function checkStream(){
    var xhr1 = new XMLHttpRequest();
    xhr1.open("POST", "https://id.twitch.tv/oauth2/token?client_id=...", true);
    xhr1.onreadystatechange = function() {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            var token = JSON.parse(xhr1.responseText);

            var xhr = new XMLHttpRequest();
            xhr.open("GET", "https://api.twitch.tv/helix/streams?user_login=skyyart", true);
            xhr.setRequestHeader("Client-ID", "mysh0atfagb466zkik8z5yy9nbs8ej");
            xhr.setRequestHeader("Authorization", "Bearer " + token["access_token"]);
            xhr.onreadystatechange = function(){
                if(xhr.readyState == 4){
                    var data = JSON.parse(xhr.responseText); // Data from Twitch API

                    if(data["data"][0] != null){
                        // Uses game_id from Twitch API response to make another API call
                        var xhrjeu = new XMLHttpRequest();
                        xhrjeu.open("GET", "https://api.twitch.tv/helix/games?id=" + data["data"][0]["game_id"], true);
                        // Makes request to hardcoded Twitch API
                    }
                }
            }
            xhr.send();
        }
    }
    xhr1.send();
}

// Runs automatically every 30 seconds
setInterval(function(){
    checkStream();
}, 30000);
```

**Classification:** FALSE POSITIVE

**Reason:** This is internal extension logic with no external attacker trigger. The flow involves data FROM the hardcoded Twitch API backend (api.twitch.tv) being used TO make another request to the same hardcoded Twitch API backend. This is trusted infrastructure communication. The extension automatically polls Twitch's API to check stream status - there is no way for an external attacker to trigger or control this flow. The data comes from and goes to developer's trusted backend servers (Twitch API in this case).

---
