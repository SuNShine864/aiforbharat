window.evaluateBidder = function (bidderId) {

    const btn = document.querySelector(
        `[data-bidder="${bidderId}"]`
    );

    btn.innerText = "Processing...";

    btn.disabled = true;

    showToast("Extracting document text...");
    setTimeout(() => {

    showToast("Generating embeddings...");

}, 15000);


setTimeout(() => {

    showToast("Storing vectors in Pinecone...");

}, 59000);


setTimeout(() => {

    showToast("Running AI evaluation...");

}, 60000);


setTimeout(() => {

    btn.innerText = "View Report";

    btn.disabled = false;

    btn.setAttribute(
        "onclick",
        "viewReport()"
    );

    showToast("Evaluation Complete");

}, 59000);
};


window.viewReport = function () {

    const modal =
        document.getElementById("evaluationModal");

    const content =
        document.getElementById("evaluationContent");

    content.innerHTML = `

        <p>
            <strong>Bidder:</strong>
            ABC Infrastructure Pvt Ltd
        </p>

        <p>
            <strong>Status:</strong>
            MANUAL REVIEW
        </p>

        <table class="evaluation-table">

            <thead>

                <tr>
                    <th>Criterion</th>
                    <th>Required</th>
                    <th>Found</th>
                    <th>AI Verdict</th>
                    <th>Human Verdict</th>
                    <th>Page</th>
                </tr>

            </thead>

            <tbody>

                <tr>
                    <td>GST Certificate</td>
                    <td>Mandatory</td>
                    <td>Available</td>
                    <td>ELIGIBLE</td>

<td>

    <select class="verdict-dropdown">

        <option>ELIGIBLE</option>

        <option>NOT ELIGIBLE</option>

    </select>

</td>
                    <td>3</td>
                </tr>

                <tr>
                    <td>Annual Turnover</td>
                    <td>₹5 Crore</td>
                    <td>₹7.8 Crore</td>
                    <td>ELIGIBLE</td>

<td>

    <select class="verdict-dropdown">

        <option>ELIGIBLE</option>

        <option>NOT ELIGIBLE</option>

    </select>

</td>
                    <td>1</td>
                </tr>

                <tr>
                    <td>Past Experience</td>
                    <td>3 Projects</td>
                    <td>4 Projects</td>
                    <td>ELIGIBLE</td>

<td>

    <select class="verdict-dropdown">

        <option>ELIGIBLE</option>

        <option>NOT ELIGIBLE</option>

    </select>

</td>
                    <td>2</td>
                </tr>

                <tr>
                    <td>Bank Solvency</td>
                    <td>₹2 Crore</td>
                    <td>₹3 Crore</td>
                    <td>MANUAL REVIEW</td>

<td>

    <select class="verdict-dropdown">

        <option>ELIGIBLE</option>

        <option>NOT ELIGIBLE</option>

    </select>

</td>
                    <td>5</td>
                </tr>

            </tbody>

        </table>
    `;

    modal.classList.remove("hidden");
};




window.addEventListener("DOMContentLoaded", () => {

    document
        .getElementById("closeModal")
        .addEventListener("click", () => {

            document
                .getElementById("evaluationModal")
                .classList.add("hidden");
        });

});