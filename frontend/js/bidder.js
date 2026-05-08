async function submitBid() {
        const files = document.getElementById('b-files').files;
        if(files.length === 0) return alert("Select files.");
        const formData = new FormData();
        for(let f of files) formData.append('files', f);
        document.getElementById('loader').style.display = 'flex';
        try {
            await fetch(`/tenders/${currentTenderId}/bidders/1/upload`, { method: 'POST', body: formData });
            showToast("Submission Processing Complete.");
            navigate('eval-tenders');
        } catch (e) { showToast("Upload failed."); }
        finally { document.getElementById('loader').style.display = 'none'; }
    }
async function evaluateBidder(
    bidderId
) {

    showToast("Evaluating bidder...");

    const response = await fetch(

        `https://aiforbharat-backend.onrender.com/bidder/evaluate/${bidderId}`,

        {
            method: "POST"
        }
    );

    const data = await response.json();

    console.log(data);

    showToast("Evaluation complete");

    openEvaluationModal({

    bidder_name: "ABC Infrastructure Pvt Ltd",

    overall_status: "ELIGIBLE",

    criteria_results: data.results
});
}
async function loadSubmissions() {

    const response = await fetch(
        "https://aiforbharat-backend.onrender.com/bidder/submissions"
    );

    const data = await response.json();

    console.log(data);

    const container =
        document.getElementById("content");

    container.innerHTML = `

        <table class="submission-table">

            <thead>
                <tr>
                    <th>Bidder Name</th>
                    <th>Tender ID</th>
                    <th>Status</th>
                </tr>
            </thead>

            <tbody>

                ${data.map(item => `

                    <tr>

                        <td>${item.bidder_name}</td>

                        <td>${item.tender_id}</td>

                        <td>${item.status}</td>

                    </tr>

                `).join("")}

            </tbody>

        </table>
    `;
}
async function viewReport(
    bidderId
) {

    navigate("bidder-report-page");

    const res = await fetch(
        `https://aiforbharat-backend.onrender.com/bidder/${bidderId}`
    );

    const bidder = await res.json();

    const tbody = document.getElementById(
        "report-table-body"
    );

    tbody.innerHTML = "";

    bidder.results.forEach(r => {

        tbody.innerHTML += `

        <tr>

            <td>
                ${r.criterion_id}
            </td>

            <td>
                ${r.required || "-"}
            </td>

            <td>
                ${r.value || "-"}
            </td>

            <td>
                ${r.verdict}
            </td>

            <td>
                ${r.page || "-"}
            </td>

        </tr>
        `;
    });
}
function downloadTender(tenderId) {

    window.open(

        `https://aiforbharat-backend.onrender.com/tender/download/${tenderId}`,

        "_blank"
    );
}
function openBidSubmission(tenderId) {

    // open upload page
    navigate('bidder-upload');

    // store tender id
    document.getElementById(
        'selected-tender-id'
    ).value = tenderId;

    console.log("Selected Tender:", tenderId);
}
async function renderBidderTenders() {

    try {

        const res = await fetch(
            "https://aiforbharat-backend.onrender.com/tender"
        );

        const tenders = await res.json();

        const tbody = document.getElementById(
            "bidder-tender-list"
        );

        tbody.innerHTML = "";

        tenders.forEach(t => {

            tbody.innerHTML += `

            <tr>

                <td>
                    <strong>${t.tender_id}</strong>
                </td>

                <td>
                    ${t.tender_name || "Untitled Tender"}
                </td>

                <td>
                    15 May 2026
                </td>

                <td>
                    <button
                        class="btn btn-outline btn-sm"
                        onclick="downloadTender('${t.tender_id}')"
                    >
                        Download
                    </button>
                    <button 
                        class="btn btn-primary btn-sm"
                        onclick="openBidSubmission('${t.tender_id}')"
                    >
                        Apply Now
                    </button>

                </td>

            </tr>
            `;
        });

    } catch (err) {

        console.error(err);

        showToast("Failed to load tenders");
    }
}
async function submitBid() {

    const tenderId = document.getElementById(
        'selected-tender-id'
    ).value;

    const bidderName = document.getElementById(
        'bidder-name'
    ).value;

    const files = document.getElementById(
        'b-files'
    ).files;

    const formData = new FormData();

    formData.append("tender_id", tenderId);

    formData.append("bidder_name", bidderName);

    for (let file of files) {

        formData.append("files", file);
    }

    try {

        const res = await fetch(
            "https://aiforbharat-backend.onrender.com/bidder/upload",
            {
                method: "POST",
                body: formData
            }
        );

        const data = await res.json();

        console.log(data);

        alert("Bid submitted successfully");

    } catch (err) {

        console.error(err);

        alert("Upload failed");
    }
}
renderBidderTenders();
