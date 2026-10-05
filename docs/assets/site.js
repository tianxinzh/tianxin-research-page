// Progressive enhancement only. All paper content and citations are in HTML.
document.querySelectorAll('[data-copy-citation]').forEach((button) => {
  button.hidden = false;
  button.addEventListener('click', async () => {
    const citation = document.getElementById(button.dataset.copyCitation);
    const status = button.closest('.citation-box').querySelector('[role="status"]');
    try {
      if (!navigator.clipboard || !window.isSecureContext) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(citation.textContent);
      status.textContent = 'Citation copied.';
    } catch {
      status.textContent = 'Copy is unavailable here. Select the citation text or download the BibTeX file.';
    }
  });
});
