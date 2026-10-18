(function() {
    'use strict';

    if (!navigator.clipboard) return;

    const copyButtonLabel = '📋';
    const copiedButtonLabel = '✅';

    function addCopyButtons() {
        const highlights = document.querySelectorAll('.highlight');

        highlights.forEach(highlight => {
            // Create the button
            const button = document.createElement('button');
            button.className = 'copy-code-button';
            button.type = 'button';
            button.innerText = copyButtonLabel;

            // Find the code element to copy from
            // Hugo adds a table if line numbers are enabled
            let codeBlock = highlight.querySelector('td:last-child code');
            if (!codeBlock) {
                codeBlock = highlight.querySelector('code');
            }

            if (!codeBlock) return;

            button.addEventListener('click', async () => {
                try {
                    // Extract text content. innerText is usually better for code fragments
                    // to preserve whitespace correctly but avoid hidden elements.
                    const textToCopy = codeBlock.innerText;
                    await navigator.clipboard.writeText(textToCopy);

                    button.innerText = copiedButtonLabel;
                    button.classList.add('copied');

                    setTimeout(() => {
                        button.innerText = copyButtonLabel;
                        button.classList.remove('copied');
                    }, 2000);
                } catch (err) {
                    console.error('Failed to copy text: ', err);
                    button.innerText = 'Error';
                }
            });

            // Ensure the container is relative so we can position the button
            highlight.style.position = 'relative';
            highlight.appendChild(button);
        });
    }

    // Run after DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', addCopyButtons);
    } else {
        addCopyButtons();
    }
})();
