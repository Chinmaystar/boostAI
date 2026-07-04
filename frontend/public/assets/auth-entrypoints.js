(function () {
  var patched = new WeakSet();
  var fallbackId = "boostai-auth-fallback";

  function buildAuthUrl(mode) {
    var params = new URLSearchParams();
    params.set("mode", mode);
    params.set("returnTo", window.location.pathname + window.location.search + window.location.hash);
    return "/login.html?" + params.toString();
  }

  function normalizedText(node) {
    return (node.textContent || "").trim().toLowerCase().replace(/\s+/g, " ");
  }

  function classify(text) {
    if (text === "login" || text === "log in") return "login";
    if (
      text === "sign up" ||
      text === "start free" ||
      text === "try for free" ||
      text === "get started" ||
      text === "create account"
    ) return "signup";
    return null;
  }

  function applyLink(node, kind) {
    if (patched.has(node)) return;
    node.href = buildAuthUrl(kind === "login" ? "login" : "signup");
    node.target = "_self";
    node.setAttribute("data-boostai-auth-patched", "true");
    patched.add(node);
  }

  function patchLinks(root) {
    var foundAuth = false;
    var links = root.querySelectorAll("a");

    links.forEach(function (link) {
      var kind = classify(normalizedText(link));
      if (!kind) return;
      applyLink(link, kind);
      foundAuth = true;
    });

    return foundAuth;
  }

  function ensureFallback() {
    if (document.getElementById(fallbackId)) return;

    var wrap = document.createElement("div");
    wrap.id = fallbackId;
    wrap.setAttribute("style", [
      "position:fixed",
      "right:16px",
      "bottom:16px",
      "z-index:9999",
      "display:flex",
      "gap:10px",
      "align-items:center"
    ].join(";"));

    var login = document.createElement("a");
    login.href = buildAuthUrl("login");
    login.textContent = "Login";
    login.setAttribute("style", [
      "display:inline-flex",
      "align-items:center",
      "justify-content:center",
      "padding:12px 16px",
      "border-radius:999px",
      "background:rgba(255,255,255,0.92)",
      "border:1px solid rgba(16,33,63,0.12)",
      "box-shadow:0 12px 28px rgba(16,33,63,0.10)",
      "color:#10213f",
      "font:600 14px/1 Sundry, Helvetica Neue, sans-serif",
      "text-decoration:none"
    ].join(";"));

    var signup = document.createElement("a");
    signup.href = buildAuthUrl("signup");
    signup.textContent = "Sign up";
    signup.setAttribute("style", [
      "display:inline-flex",
      "align-items:center",
      "justify-content:center",
      "padding:12px 16px",
      "border-radius:999px",
      "background:linear-gradient(135deg,#2f68ff 0%,#5a93ff 100%)",
      "box-shadow:0 12px 28px rgba(47,104,255,0.22)",
      "color:#fff",
      "font:700 14px/1 Sundry, Helvetica Neue, sans-serif",
      "text-decoration:none"
    ].join(";"));

    wrap.appendChild(login);
    wrap.appendChild(signup);
    document.body.appendChild(wrap);
  }

  function run() {
    var found = patchLinks(document);
    if (!found) ensureFallback();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run, { once: true });
  } else {
    run();
  }

  var observer = new MutationObserver(function () {
    var found = patchLinks(document);
    if (found) {
      var fallback = document.getElementById(fallbackId);
      if (fallback) fallback.remove();
    }
  });

  observer.observe(document.documentElement, {
    childList: true,
    subtree: true
  });
}());
