(function () {
  var isFile = window.location.protocol === "file:";
  var resolveLocal = typeof window.__boostAiResolveLocalPath === "function"
    ? window.__boostAiResolveLocalPath
    : function (href) { return href; };
  var INTERNAL_HOSTS = new Set([window.location.hostname, "", "boostai.study", "www.boostai.study"]);
  var path = currentPath();
  var isSchool = path === "/school/";
  var isUni = path === "/uni/" || path === "/university/";
  var isStudy = path === "/study/";
  var isPractice = path === "/practice/";

  function currentPath() {
    if (!isFile) {
      return canonicalPath(window.location.pathname);
    }

    var pathname = window.location.pathname.replace(/\\/g, "/");
    var fileMatch = pathname.match(/\/(school|uni|university|study|practice|auth|account|library)\/index\.html$/i);
    if (fileMatch) {
      return canonicalPath("/" + fileMatch[1] + "/");
    }

    if (/\/index\.html$/i.test(pathname)) {
      return "/";
    }

    return canonicalPath(pathname);
  }

  function canonicalPath(input) {
    var next = input || "/";
    next = next.replace(/\/index\.html$/i, "/");
    next = next.replace(/\/university\/?$/i, "/uni/");
    if (!next.endsWith("/")) {
      next += "/";
    }
    if (next === "//") {
      next = "/";
    }
    return next;
  }

  function normalizeHref(rawHref) {
    if (!rawHref || rawHref === "#") {
      return rawHref;
    }

    if (isFile) {
      return resolveLocal(rawHref);
    }

    try {
      var url = new URL(rawHref, window.location.origin);
      if (!INTERNAL_HOSTS.has(url.hostname)) {
        return rawHref;
      }

      var nextPath = canonicalPath(url.pathname);
      return nextPath + url.search + url.hash;
    } catch (error) {
      return rawHref;
    }
  }

  function isSameRoute(targetHref) {
    if (isFile) {
      return false;
    }

    try {
      var url = new URL(targetHref, window.location.origin);
      return canonicalPath(url.pathname) === path && url.search === window.location.search && url.hash === window.location.hash;
    } catch (error) {
      return false;
    }
  }

  function normalizeLinks(root) {
    Array.prototype.forEach.call(root.querySelectorAll("a[href]"), function (link) {
      var next = normalizeHref(link.getAttribute("href"));
      if (next && next !== link.getAttribute("href")) {
        link.setAttribute("href", next);
      }
    });
  }

  function smoothNavigate(href) {
    if (!href || isSameRoute(href)) {
      return;
    }

    document.body.classList.add("boostai-page-leaving");
    window.setTimeout(function () {
      window.location.href = isFile ? resolveLocal(href) : href;
    }, 150);
  }

  function interceptInternalLinks(event) {
    var link = event.target && event.target.closest ? event.target.closest("a[href]") : null;
    if (!link) return;
    if (link.target && link.target !== "_self") return;
    if (link.hasAttribute("download")) return;
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;

    var href = normalizeHref(link.getAttribute("href"));
    if (!href) return;

    try {
      var url = new URL(href, isFile ? window.location.href : window.location.origin);
      if (!INTERNAL_HOSTS.has(url.hostname)) return;
      event.preventDefault();
      smoothNavigate(isFile ? href : url.pathname + url.search + url.hash);
    } catch (error) {
      return;
    }
  }

  function createLink(label, href, className, active) {
    var link = document.createElement("a");
    link.className = "boostai-context-link" + (className ? " " + className : "") + (active ? " is-active" : "");
    link.href = isFile ? resolveLocal(href) : href;
    link.textContent = label;
    return link;
  }

  function mountDock() {
    if (!(isSchool || isUni || isStudy || isPractice)) {
      return;
    }

    if (document.querySelector(".boostai-context-dock")) {
      return;
    }

    var dock = document.createElement("div");
    dock.className = "boostai-context-dock";

    var label = document.createElement("div");
    label.className = "boostai-context-label";
    label.textContent = "Switch experience";
    dock.appendChild(label);

    var links = document.createElement("div");
    links.className = "boostai-context-links";
    links.appendChild(createLink("School", "/school/", "", isSchool));
    links.appendChild(createLink("University", "/uni/", "is-uni", isUni));
    links.appendChild(createLink("Practice Bank", "/practice/?context=school&subject=maths", "", isPractice));

    dock.appendChild(links);
    document.body.appendChild(dock);
    document.body.classList.add("boostai-has-dock");
  }

  function mountStudyBanner() {
    if (!isStudy || document.querySelector(".boostai-context-banner")) {
      return;
    }

    var params = new URLSearchParams(window.location.search);
    var context = params.get("context");
    if (!context) {
      return;
    }

    var shell = document.querySelector(".shell");
    if (!shell) {
      return;
    }

    var banner = document.createElement("section");
    banner.className = "boostai-context-banner";

    var title = document.createElement("strong");
    title.textContent = context === "university"
      ? "University context is live in the study workspace"
      : "School context is live in the study workspace";

    var copy = document.createElement("p");
    copy.textContent = context === "university"
      ? "This route keeps the university landing connected to the study demo while staying inside the same static site."
      : "This route now connects the school landing, the study demo, and the practice bank so the flow feels like one product.";

    var actions = document.createElement("div");
    actions.className = "boostai-context-links";
    actions.appendChild(createLink(context === "university" ? "Back to university" : "Back to school", context === "university" ? "/uni/" : "/school/"));

    if (context !== "university") {
      actions.appendChild(createLink("Open practice bank", "/practice/?context=school&subject=maths"));
    }

    banner.appendChild(title);
    banner.appendChild(copy);
    banner.appendChild(actions);
    shell.insertBefore(banner, shell.children[1] || null);
  }

  function ready() {
    var mainShell = document.getElementById("root") || document.querySelector(".shell") || document.body;
    mainShell.classList.add("boostai-page-shell");
    window.requestAnimationFrame(function () {
      mainShell.classList.add("boostai-ready");
    });

    normalizeLinks(document);
    mountDock();
    mountStudyBanner();

    var observer = new MutationObserver(function () {
      normalizeLinks(document);
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }

  document.addEventListener("click", interceptInternalLinks);
  document.addEventListener("DOMContentLoaded", ready);
}());
