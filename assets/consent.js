(function () {
  var KEY = "wfb_consent";
  var banner = null;
  function read() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }
  function save(value) {
    try { localStorage.setItem(KEY, value); } catch (e) {}
  }
  function apply(granted) {
    save(granted ? "granted" : "denied");
    if (banner) banner.hidden = true;
    if (typeof window.setGA4Consent === "function") window.setGA4Consent(granted);
  }
  function show() {
    if (!banner) {
      banner = document.createElement("div");
      banner.className = "consent";
      banner.setAttribute("role", "dialog");
      banner.setAttribute("aria-label", "Cookie settings");
      banner.innerHTML = '<p>Google Analytics 4 stays off until you accept. Cloudflare Web Analytics does not use cookies. <a href="/privacy/">Privacy</a></p>'
        + '<p class="consent-actions"><button type="button" class="accept">Accept</button><button type="button" class="reject">Reject</button></p>';
      document.body.appendChild(banner);
      banner.querySelector(".accept").addEventListener("click", function () { apply(true); });
      banner.querySelector(".reject").addEventListener("click", function () { apply(false); });
    }
    banner.hidden = false;
  }
  var link = document.getElementById("cookie-settings");
  if (link) {
    link.addEventListener("click", function (e) {
      e.preventDefault();
      show();
    });
  }
  var saved = read();
  if (saved === "granted") {
    if (typeof window.setGA4Consent === "function") window.setGA4Consent(true);
  } else if (saved !== "denied") {
    show();
  }
})();
