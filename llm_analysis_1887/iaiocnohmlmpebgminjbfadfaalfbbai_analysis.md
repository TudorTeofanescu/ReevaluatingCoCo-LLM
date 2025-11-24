# CoCo Analysis: iaiocnohmlmpebgminjbfadfaalfbbai

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** Multiple (all same pattern - XMLHttpRequest → JQ_obj_html_sink)

---

## Sink: XMLHttpRequest_responseText_source → JQ_obj_html_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/iaiocnohmlmpebgminjbfadfaalfbbai/opgen_generated_files/bg.js
Line 332: XMLHttpRequest.prototype.responseText = 'sensitive_responseText'
Line 3966: var data = JSON.parse(xhr.responseText);
Line 3968: handleDataReturn(data.data);
Line 3924: key = KEYS_TWITCH[data[i]['user_id']];
Line 4016: retour += getGame(key);
Line 4073: $("#content_twitch_"+key).html(textePopup);

**Code:**

```javascript
// Background script bg.js - Hardcoded API URLs (Lines 3306-3379)
const URL_PCS_API = "https://my.project-conquerors.com/web/load/?exs=extension_info&type=json";
const URL_PCS_API_TRN = "https://my.project-conquerors.com/web/load/?exs=extension_tournoi&type=json";
const URL_PCS_WP_RSS = "https://my.project-conquerors.com/web/load/?exs=extension_news&type=json";
const URL_PCS_YT = "https://my.project-conquerors.com/web/load/?exs=extension_youtube&type=json";
const URL_PCS_TWITCH_API = "https://my.project-conquerors.com/web/load/?exs=extension_twitch&type=json";

// XHR request to hardcoded backend (Lines 3958-3978)
var xhr = new XMLHttpRequest();
var url = URL_PCS_TWITCH_API + "&parameters="+ parameters; // ← Hardcoded backend URL
xhr.open("GET", url, true);
xhr.onload = function() {
    if (xhr.status >= 200 && xhr.status < 400) {
        var data = JSON.parse(xhr.responseText); // ← Data from trusted backend
        handleDataReturn(data.data);
    }
}
xhr.send(null);

// Data processing and rendering (Lines 3920-4073)
function handleDataReturn(data) {
    var key = "";
    for (var i = 0; i < data.length; i++) {
        key = KEYS_TWITCH[data[i]['user_id']];
        if (data[i] && KEYS.includes(key)) {
            dataStream[key] = data[i]; // ← Store data from trusted backend
            online(key);
        }
    }
}

function online(key) {
    var twitchtitre = dataStream[key].title; // ← Data from trusted backend
    var textePopup = getTextePopup(key, newtitre, pseudo);
    $("#content_twitch_"+key).html(textePopup); // ← Render in popup
}

function getTextePopup(key, newTitre, pseudo) {
    var retour = newTitre;
    retour += "<br/>";
    retour += '<span class="label label-default">';
    retour += getGame(key); // ← Uses dataStream from trusted backend
    retour += '</span>&nbsp;';
    // ... builds HTML from backend data
    return retour;
}

function getGame(key) {
    return dataStream[key].game.name; // ← Data from trusted backend
}
```

**Classification:** FALSE POSITIVE

**Reason:** The extension fetches data exclusively from hardcoded backend URLs (my.project-conquerors.com), which is the developer's trusted infrastructure. All API endpoints are hardcoded constants, and the data flowing to the jQuery .html() sink originates entirely from these developer-controlled backend servers. While .html() can be a sink for XSS vulnerabilities, the data source is not attacker-controlled. According to the methodology, "Data FROM hardcoded backend: fetch('https://api.myextension.com') → response → rendering" is a FALSE POSITIVE, as "Developer trusts their own infrastructure; compromising it is infrastructure issue, not extension vulnerability." An attacker would need to compromise the backend infrastructure (my.project-conquerors.com) to exploit this, which is outside the scope of extension vulnerabilities.
