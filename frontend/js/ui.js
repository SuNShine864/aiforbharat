lucide.createIcons();
let currentTenderId = null;

function showToast(msg) { const t = document.getElementById('toast'); t.innerText = msg; t.style.display = 'block'; setTimeout(() => t.style.display = 'none', 3000); }

function setRole(role) {
    document.body.setAttribute('data-role', role);
    navigate(role === 'evaluator' ? 'eval-tenders' : (role === 'bidder' ? 'bidder-list' : 'audit-logs'));
    showToast(`Switched to ${role.toUpperCase()} mode`);
}

function navigate(pageId, id = null) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    const target = document.getElementById(pageId);
    if (target) target.classList.add('active');
    if (document.getElementById('nav-' + pageId)) document.getElementById('nav-' + pageId).classList.add('active');
    if (id) currentTenderId = id;
    if (pageId === 'eval-tenders') renderTenders();
    if (pageId === 'eval-matrix') renderMatrix();
    if (pageId === 'bidder-list') renderBidderTenders();
    if (pageId === 'audit-logs') renderAuditLogs();
    closeInspector();
}
function closeInspector() { document.getElementById('inspector').classList.remove('open'); }
window.onload = () => navigate('eval-tenders');
window.viewReport = async function (bidderId) {

    console.log("Viewing report:", bidderId);

    // Later this will come from backend/database

    const mockResult = {
        bidder_name: "ABC Pvt Ltd",

        ai_status: "Eligible",

        criteria_results: [
            {
                criteria: "GST Certificate",
                required: "Mandatory",
                found: "Yes",
                result: "Pass"
            },

            {
                criteria: "Turnover",
                required: "50 Lakhs",
                found: "60 Lakhs",
                result: "Pass"
            }
        ]
    };

    openEvaluationModal(mockResult);
};
window.evaluateBidder = async function (bidderId) {

    console.log("Evaluating:", bidderId);

    // MOCK RESPONSE FOR NOW

    const mockResult = {
        bidder_name: "ABC Pvt Ltd",

        ai_status: "Manual Review",

        criteria_results: [
            {
                criteria: "GST Certificate",
                required: "Mandatory",
                found: "Yes",
                result: "Pass"
            },

            {
                criteria: "Turnover",
                required: "50 Lakhs",
                found: "42 Lakhs",
                result: "Fail"
            },

            {
                criteria: "Experience",
                required: "3 Years",
                found: "4 Years",
                result: "Pass"
            }
        ]
    };

    openEvaluationModal(mockResult);
};
function openEvaluationModal(data) {

    const modal = document.getElementById("evaluationModal");

    const content =
        document.getElementById("evaluationContent");

    content.innerHTML = `

        <p>
            <strong>Bidder:</strong>
            ${data.bidder_name}
        </p>

        <p>
            <strong>AI Status:</strong>
            ${data.overall_status}
        </p>

        <table class="evaluation-table">

            <thead>
        <tr>
        <th>Criterion</th>
        <th>Required</th>
        <th>Found</th>
        <th>Verdict</th>
        <th>Page</th>
        </tr>
    </thead>

            <tbody>

${data.criteria_results.map(item => `

<tr>
    <td>${item.criterion}</td>
    <td>${item.required}</td>
    <td>${item.found}</td>
    <td>${item.verdict}</td>
    <td>${item.page}</td>
</tr>

`).join("")}

</tbody>

        </table>

        <div class="decision-section">

            <h3>Final Decision</h3>

            <select id="finalStatus">

                <option>Eligible</option>

                <option>Not Eligible</option>

                <option selected>
                    Manual Review
                </option>

            </select>

            <textarea
                id="reviewNotes"
                placeholder="Reviewer notes..."
            ></textarea>

            <button id="saveDecisionBtn">

                Save Decision

            </button>

        </div>
    `;

    modal.classList.remove("hidden");
}
document
    .getElementById("closeModal")
    .addEventListener("click", () => {

        document
            .getElementById("evaluationModal")
            .classList.add("hidden");
    });