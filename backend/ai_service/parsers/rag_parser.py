from ai_service.rag.retriever import (
    retrieve_relevant_chunks
)

from ai_service.rag.evaluator import (
    evaluate_criterion
)

def run_rag_evaluation(

    bidder_id,

    criteria
):

    results = []

    for criterion in criteria:

        chunks = retrieve_relevant_chunks(

            bidder_id,

            criterion["description"],

            top_k=5
        )

        result = evaluate_criterion(

            criterion,

            chunks
        )

        results.append(result)

    return results