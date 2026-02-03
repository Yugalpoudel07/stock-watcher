// Regex to detect potential tickers (with or without $)
const tickerRegex = /\$?[A-Z]{1,5}/g;

// Cache to store API results for already fetched tickers
const tickerCache = {};

// Walk through text nodes safely
function walkTextNodes(node) {
    if (node.nodeType === Node.TEXT_NODE) {
        const parent = node.parentNode;
        const frag = document.createDocumentFragment();
        let lastIndex = 0;
        const text = node.textContent;

        text.replace(tickerRegex, (match, index) => {
            // Add text before match
            frag.appendChild(document.createTextNode(text.slice(lastIndex, index)));

            // Create span for ticker
            const span = document.createElement("span");
            span.className = "ticker";
            span.style.color = "blue";
            span.style.cursor = "pointer";
            span.textContent = match;
            frag.appendChild(span);

            lastIndex = index + match.length;
        });

        // Add remaining text
        frag.appendChild(document.createTextNode(text.slice(lastIndex)));

        parent.replaceChild(frag, node);
    } else if (node.nodeType === Node.ELEMENT_NODE && node.nodeName !== "SCRIPT" && node.nodeName !== "STYLE" && node.nodeName !== "TEXTAREA") {
        for (let child of Array.from(node.childNodes)) {
            walkTextNodes(child);
        }
    }
}

// Start processing the body
walkTextNodes(document.body);

// Function to show tooltip
function showTooltip(elem, data) {
    // Remove existing tooltips
    const existing = document.querySelector(".stock-tooltip");
    if (existing) existing.remove();

    const tooltip = document.createElement("div");
    tooltip.className = "stock-tooltip";
    tooltip.style.position = "absolute";
    tooltip.style.background = "#fff";
    tooltip.style.border = "1px solid #333";
    tooltip.style.padding = "8px";
    tooltip.style.zIndex = 9999;
    tooltip.style.borderRadius = "4px";
    tooltip.style.boxShadow = "0 2px 6px rgba(0,0,0,0.2)";
    tooltip.style.fontSize = "13px";
    tooltip.style.maxWidth = "220px";

    const price3m = data.future_predictions['3 months'];
    const color = price3m >= data.price ? "green" : "red";

    tooltip.innerHTML = `
        <strong>${data.ticker}</strong><br>
        Current: $${data.price.toFixed(2)}<br>
        <span style="color:${color}">3m: $${price3m.toFixed(2)}</span><br>
        6m: $${data.future_predictions['6 months'].toFixed(2)}<br>
        9m: $${data.future_predictions['9 months'].toFixed(2)}<br>
        12m: $${data.future_predictions['12 months'].toFixed(2)}
    `;

    document.body.appendChild(tooltip);

    // Position tooltip
    const rect = elem.getBoundingClientRect();
    tooltip.style.top = rect.bottom + window.scrollY + "px";
    tooltip.style.left = rect.left + window.scrollX + "px";

    // Remove tooltip on mouse leave
    elem.addEventListener("mouseleave", () => {
        tooltip.remove();
    });
}

// Hover event for tickers
document.addEventListener("mouseover", async (e) => {
    if (e.target.classList.contains("ticker")) {
        const symbol = e.target.innerText.replace('$', '').toUpperCase();

        // If cached, show tooltip
        if (tickerCache[symbol]) {
            showTooltip(e.target, tickerCache[symbol]);
            return;
        }

        try {
            const response = await fetch(`http://127.0.0.1:5000/get_stock_info?ticker=${symbol}`);
            const data = await response.json();

            if (!data.error) {
                tickerCache[symbol] = data; // Cache for later
                showTooltip(e.target, data);
            }
        } catch (err) {
            console.error("Error fetching ticker info:", err);
        }
    }
});
