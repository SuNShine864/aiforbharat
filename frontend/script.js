
    async function renderBidderTenders() {
        const res = await fetch('/tenders/');
        const tenders = await res.json();
        document.getElementById('bidder-list-body').innerHTML = tenders.map(t => `
            <tr><td>T${t.id}</td><td>${t.name}</td><td>15 May 2026</td>
            <td><button class="btn btn-primary btn-sm" onclick="navigate('bidder-upload', ${t.id})">Apply Now</button></td></tr>
        `).join('');
    }