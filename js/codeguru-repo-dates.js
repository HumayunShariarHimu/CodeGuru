(function () {
  "use strict";

  var owner = "HumayunShariarHimu";
  var cards = Array.prototype.slice.call(document.querySelectorAll(".course[data-repo]"));
  if (!cards.length) return;

  var targets = Object.create(null);
  cards.forEach(function (card) {
    var slug = (card.getAttribute("data-repo") || "").toLowerCase();
    var status = card.querySelector(".card-footer .text-muted");
    if (!slug || !status) return;
    targets[slug] = {
      element: status,
      url: "https://github.com/" + owner + "/" + encodeURIComponent(slug)
    };
    status.setAttribute("aria-live", "polite");
  });

  var slugs = Object.keys(targets);
  if (!slugs.length) return;

  var cacheKey = "codeguru-public-repository-dates-v1";
  var cacheMaxAge = 5 * 60 * 1000;

  function relativeTime(isoDate) {
    if (window.moment) {
      var momentDate = window.moment(isoDate);
      if (momentDate.isValid()) return momentDate.locale("bn").fromNow();
    }

    var date = new Date(isoDate);
    if (isNaN(date.getTime())) return null;
    if (window.Intl && Intl.RelativeTimeFormat) {
      var seconds = (date.getTime() - Date.now()) / 1000;
      var units = [
        ["year", 31536000],
        ["month", 2592000],
        ["week", 604800],
        ["day", 86400],
        ["hour", 3600],
        ["minute", 60],
        ["second", 1]
      ];
      var formatter = new Intl.RelativeTimeFormat("bn", { numeric: "auto" });
      for (var i = 0; i < units.length; i += 1) {
        if (Math.abs(seconds) >= units[i][1] || units[i][0] === "second") {
          return formatter.format(Math.round(seconds / units[i][1]), units[i][0]);
        }
      }
    }
    return date.toLocaleDateString("bn-BD");
  }

  function renderDates(repoDates) {
    slugs.forEach(function (slug) {
      var target = targets[slug];
      var pushedAt = repoDates[slug];
      var relative = pushedAt && relativeTime(pushedAt);
      if (relative) {
        target.element.textContent = "হালনাগাদ হয়েছে " + relative;
        target.element.title = new Date(pushedAt).toLocaleString("bn-BD");
        return;
      }
      target.element.textContent = "সর্বশেষ হালনাগাদ: ";
      var link = document.createElement("a");
      link.href = target.url;
      link.rel = "noopener noreferrer";
      link.textContent = "GitHub";
      target.element.appendChild(link);
    });
  }

  function isComplete(repoDates) {
    return slugs.every(function (slug) {
      return Object.prototype.hasOwnProperty.call(repoDates, slug);
    });
  }

  function readCache() {
    try {
      var cached = JSON.parse(window.sessionStorage.getItem(cacheKey) || "null");
      if (cached && cached.savedAt && Date.now() - cached.savedAt < cacheMaxAge && isComplete(cached.dates)) {
        return cached.dates;
      }
    } catch (error) {
      // Storage can be unavailable in privacy-restricted browser contexts.
    }
    return null;
  }

  function saveCache(repoDates) {
    try {
      window.sessionStorage.setItem(cacheKey, JSON.stringify({ savedAt: Date.now(), dates: repoDates }));
    } catch (error) {
      // The widget remains functional when session storage is unavailable.
    }
  }

  function getJson(url) {
    return window.fetch(url, {
      headers: { Accept: "application/vnd.github+json" }
    }).then(function (response) {
      if (!response.ok) throw new Error("GitHub API returned " + response.status);
      return response.json();
    });
  }

  var cachedDates = readCache();
  if (cachedDates) {
    renderDates(cachedDates);
    return;
  }

  if (!window.fetch) {
    renderDates(Object.create(null));
    return;
  }

  var listingUrl = "https://api.github.com/users/" + encodeURIComponent(owner) + "/repos?type=public&per_page=100&sort=pushed";
  getJson(listingUrl).then(function (repositories) {
    var dates = Object.create(null);
    (repositories || []).forEach(function (repo) {
      var slug = (repo.name || "").toLowerCase();
      if (targets[slug] && repo.pushed_at) dates[slug] = repo.pushed_at;
    });

    var missing = slugs.filter(function (slug) { return !dates[slug]; });
    if (!missing.length) return dates;

    return Promise.all(missing.map(function (slug) {
      var url = "https://api.github.com/repos/" + encodeURIComponent(owner) + "/" + encodeURIComponent(slug);
      return getJson(url).then(function (repo) {
        if (repo.pushed_at) dates[slug] = repo.pushed_at;
      }).catch(function () {
        // Keep a link fallback for any repository that cannot be resolved.
      });
    })).then(function () { return dates; });
  }).then(function (dates) {
    if (isComplete(dates)) saveCache(dates);
    renderDates(dates);
  }).catch(function () {
    renderDates(Object.create(null));
  });
}());
