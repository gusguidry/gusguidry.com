(function () {
  'use strict';

  const MEMES = [
    // The copypasta, each line self-contained
    "Do you have a source on that?",
    "Source? A source. I need a source.",
    "I need a source that explicitly states your argument. What you've provided is just tangential to the discussion.",
    "You can't make inferences and observations from your sources. Your comments must be a strict subset of what the sources literally say.",
    "You can't make normative statements from empirical evidence.",
    "Do you have a degree in that field? A college degree? In that field? Then your arguments are invalid.",
    "It doesn't matter how closely those data points are correlated. Correlation does not equal causation.",
    "CORRELATION. DOES. NOT. EQUAL. CAUSATION.",
    "You still haven't provided a valid source. Not even close.",
    "I just looked through all 308 pages of your user history. Figures I'm debating a glormpf supporter. A moron.",
    // Full chaos
    "Forget citing this. Tell your professor it came to you in a dream.",
    "Tell your professor your source is that you made it the f*** up.",
    "Congratulations. You've cited a personal blog. Your professor is going to love this.",
    "This is not a peer-reviewed journal. This is some guy's website.",
    "Citation copied. Your GPA was already on thin ice.",
    "A personal blog? Bold. Truly courageous academic work.",
    "You know Wikipedia has better citations than this, right?",
    "Your bibliography is going to be a disaster and I want front row seats.",
    "This counts as a primary source the same way a horoscope counts as a weather forecast.",
    "Pasting this into your essay is going to be a great conversation starter with your academic integrity board.",
    "Your professor is going to Google this. Just so you know.",
    "Scholarly. Truly. The ivory towers tremble.",
    "If this ends up in an APA paper I'm going to need you to not tell me about it.",
    "I admire the audacity. Genuinely.",
    "At least it's not Wikipedia. It's not Wikipedia, right?",
    "Have you considered just making something up? It'd carry about the same weight.",
    "Citation successfully copied to clipboard, along with your last shred of academic credibility.",
    "Your professor has a whole folder for this kind of thing. You're about to be in it."
  ];

  function getRandomMeme() {
    return MEMES[Math.floor(Math.random() * MEMES.length)];
  }

  function showToast(message) {
    const existing = document.querySelector('.cite-toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = 'cite-toast';
    toast.setAttribute('role', 'status');
    toast.setAttribute('aria-live', 'polite');
    toast.textContent = message;
    document.body.appendChild(toast);

    // Trigger reflow for transition
    toast.getBoundingClientRect();
    toast.classList.add('cite-toast--visible');

    setTimeout(() => {
      toast.classList.remove('cite-toast--visible');
      setTimeout(() => toast.remove(), 400);
    }, 3500);
  }

  function initCite(section) {
    const tabs = section.querySelectorAll('.cite-tab');
    const panels = section.querySelectorAll('.cite-panel');
    const copyBtn = section.querySelector('.cite-copy-btn');

    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        tabs.forEach(t => { t.classList.remove('active'); t.setAttribute('aria-selected', 'false'); });
        panels.forEach(p => p.classList.remove('active'));
        tab.classList.add('active');
        tab.setAttribute('aria-selected', 'true');
        const target = section.querySelector('#cite-' + tab.dataset.target);
        if (target) target.classList.add('active');
      });
    });

    if (copyBtn && navigator.clipboard) {
      copyBtn.addEventListener('click', () => {
        const activePanel = section.querySelector('.cite-panel.active .cite-text');
        if (!activePanel) return;
        const text = activePanel.dataset.citation || activePanel.textContent;
        navigator.clipboard.writeText(text).then(() => {
          showToast(getRandomMeme());
          copyBtn.textContent = 'copied ✓';
          setTimeout(() => { copyBtn.textContent = 'copy citation'; }, 2000);
        }).catch(() => {
          copyBtn.textContent = 'failed. you\'re on your own.';
          setTimeout(() => { copyBtn.textContent = 'copy citation'; }, 2000);
        });
      });
    } else if (copyBtn) {
      copyBtn.style.display = 'none';
    }
  }

  function init() {
    document.querySelectorAll('.cite-section').forEach(initCite);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
