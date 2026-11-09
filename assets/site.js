/* Progressive enhancement: all lessons and links are already present in HTML. */
(() => {
  "use strict";
  const menuButton = document.querySelector("[data-menu-toggle]");
  const navigation = document.querySelector("[data-navigation]");
  const closeMenu = () => {
    if (!menuButton || !navigation) return;
    menuButton.setAttribute("aria-expanded", "false");
    navigation.classList.remove("is-open");
  };
  menuButton?.addEventListener("click", () => {
    const open = menuButton.getAttribute("aria-expanded") !== "true";
    menuButton.setAttribute("aria-expanded", String(open));
    navigation?.classList.toggle("is-open", open);
  });
  navigation?.querySelectorAll("a").forEach(link => link.addEventListener("click", closeMenu));
  document.addEventListener("keydown", event => {
    if (event.key === "Escape" && menuButton?.getAttribute("aria-expanded") === "true") {
      closeMenu();
      menuButton.focus();
    }
  });

  const search = document.querySelector("[data-search]");
  const cards = [...document.querySelectorAll("[data-entry]")];
  const filters = [...document.querySelectorAll("[data-filter]")];
  const resultCount = document.querySelector("[data-results-count]");
  const noResults = document.querySelector("[data-no-results]");
  let category = "全部";
  const applyFilters = () => {
    const query = (search?.value || "").trim().toLocaleLowerCase();
    let count = 0;
    cards.forEach(card => {
      const tags = JSON.parse(card.dataset.topics || "[]");
      const matches = (category === "全部" || tags.includes(category)) &&
        (!query || (card.dataset.search || "").toLocaleLowerCase().includes(query));
      card.hidden = !matches;
      if (matches) count += 1;
    });
    if (resultCount) resultCount.textContent = `共 ${count} 份资料`;
    if (noResults) noResults.hidden = count !== 0;
  };
  search?.addEventListener("input", applyFilters);
  filters.forEach(button => button.addEventListener("click", () => {
    category = button.dataset.filter;
    filters.forEach(item => item.setAttribute("aria-pressed", String(item === button)));
    applyFilters();
  }));
  document.querySelector("[data-reset-search]")?.addEventListener("click", () => {
    if (search) search.value = "";
    category = "全部";
    filters.forEach(item => item.setAttribute("aria-pressed", String(item.dataset.filter === "全部")));
    applyFilters();
    search?.focus();
  });
  if (search) {
    search.value = new URLSearchParams(location.search).get("q") || "";
    applyFilters();
  }

  document.querySelectorAll("[data-print]").forEach(button => button.addEventListener("click", () => window.print()));

  const progress = document.querySelector("[data-reading-progress]");
  if (progress) {
    let scheduled = false;
    const update = () => {
      const available = document.documentElement.scrollHeight - innerHeight;
      progress.style.width = `${available > 0 ? Math.min(100, Math.max(0, scrollY / available * 100)) : 0}%`;
      scheduled = false;
    };
    const schedule = () => {
      if (!scheduled) { scheduled = true; requestAnimationFrame(update); }
    };
    addEventListener("scroll", schedule, {passive: true});
    addEventListener("resize", schedule);
    addEventListener("load", schedule);
    schedule();
  }

  const anchors = [...document.querySelectorAll(".toc a[href^='#']")];
  if (anchors.length) {
    const targets = [...new Set(anchors.map(a => document.getElementById(a.hash.slice(1))).filter(Boolean))];
    let pending = false;
    const updateToc = () => {
      const threshold = (document.querySelector(".site-header")?.getBoundingClientRect().height || 88) + 40;
      let active = targets[0];
      targets.forEach(target => { if (target.getBoundingClientRect().top <= threshold) active = target; });
      if (active) anchors.forEach(a => a.classList.toggle("active", a.hash === `#${active.id}`));
      pending = false;
    };
    const scheduleToc = () => {
      if (!pending) { pending = true; requestAnimationFrame(updateToc); }
    };
    addEventListener("scroll", scheduleToc, {passive:true});
    addEventListener("resize", scheduleToc);
    addEventListener("load", scheduleToc);
    scheduleToc();
  }
})();
