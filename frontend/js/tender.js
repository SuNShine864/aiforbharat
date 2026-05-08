async function openSubmissions(tenderId) {

    navigate("submission-list-page");

    const res = await fetch(

        `https://aiforbharat-backend.onrender.com/bidder/tender/${tenderId}`
    );

    const data = await res.json();

    const tbody = document.getElementById(
        "submission-table-body"
    );

    tbody.innerHTML = "";

    data.bidders.forEach(b => {

        tbody.innerHTML += `

        <tr>

            <td>
                ${b.bidder_name}
            </td>

            <td>
                ${b.status || "SUBMITTED"}
            </td>

            <td>

                ${
                    b.results

                    ?

                    `
                    <button
                        class="btn btn-primary"
                        onclick="viewReport('${b.bidder_id}')"
                    >
                        View Report
                    </button>
                    `

                    :

                    `
                    <button
                        class="btn btn-primary"
                        data-bidder="${b.bidder_id}"
                        onclick="evaluateBidder('${b.bidder_id}')"
                    >   
                        Evaluate
                    </button>
                    `
                }

            </td>

        </tr>
        `;
    });
}
async function renderTenders() {

    try {

        const res = await fetch(
            "https://aiforbharat-backend.onrender.com/tender"
        );

        const tenders = await res.json();

        const tbody = document.getElementById(
            "eval-tender-list"
        );

        tbody.innerHTML = "";

        tenders.forEach(t => {

            tbody.innerHTML += `
                <tr>

                    <td>
                        <strong>${t.tender_id}</strong>
                    </td>

                    <td>
                        ${t.tender_name || t.filename || "Untitled Tender"}
                    </td>

                    <td>
                        <span class="badge badge-info">
                            ${t.status || "PUBLISHED"}
                        </span>
                    </td>

                    <td>
                        ${t.submission_count || 0} Responses
                    </td>

                    <td>
                        <button class="btn btn-outline btn-sm"
                        onclick="openSubmissions('${t.tender_id}')">
                            Submission
                        </button>

                        <button class="btn btn-outline btn-sm">
                            Audit Bundle
                        </button>
                    </td>

                </tr>
            `;
        });

    } catch (err) {

        console.log(err);

        showToast("Failed to load tenders");
    }
}
async function publishTender() {

    const name = document.getElementById('t-name').value;

    const val = document.getElementById('t-val').value;

    const file = document.getElementById('t-file').files[0];

    if (!name || !file) {
        alert("Please provide tender name and file");
        return;
    }

    const formData = new FormData();

    formData.append("title", name);
    formData.append("estimated_value", val);
    formData.append("file", file);

    // Navigate immediately
    navigate('eval-tenders');
    const tbody = document.getElementById("eval-tender-list");

tbody.innerHTML = `
<tr id="processing-row">

    <td>...</td>

    <td>${name}</td>

    <td>
        <span class="badge badge-warning">
            PROCESSING
        </span>
    </td>

    <td>
        AI extracting criteria...
    </td>

    <td>
        <button disabled>
            Processing...
        </button>
    </td>

</tr>
`;
    showToast("Processing tender...");

    try {

        const res = await fetch(
            "https://aiforbharat-backend.onrender.com/tender/upload",
            {
                method: "POST",
                body: formData
            }
        );

        const data = await res.json();

        console.log(data);

        // NOW rerender after backend completes
        await renderTenders();

        showToast("Tender published successfully");

    } catch (err) {

        console.error(err);

        showToast("Upload failed");
    }
}

    async function renderMatrix() {
        if(!currentTenderId) return;
        const res = await fetch(`/api/evaluation/${currentTenderId}/matrix`);
        const bidders = await res.json();
        document.getElementById('matrix-rows').innerHTML = bidders.map(b => `
            <tr><td><strong>${b.name}</strong><br><small>${b.category}</small></td>
            <td class="text-center"><span class="badge badge-pass">${b.overall_verdict}</span></td></tr>
        `).join('');
    }
window.addEventListener(

    "DOMContentLoaded",

    () => {

        renderTenders();
    }
);