async function renderAuditLogs() {
        const res = await fetch('/reports/1/audit-log');
        const logs = await res.json();
        document.getElementById('audit-trail').innerHTML = logs.map(l => `
            <div style="padding:10px; border-bottom:1px solid #eee; font-size:0.8rem;">
            <span style="width:120px; color:var(--gov-blue); font-weight:700;">${l.username}</span>
            <span style="width:150px; font-weight:700;">${l.action}</span>
            <span style="flex:1;">Log recorded: AI and human actions audited.</span></div>
        `).join('');
    }