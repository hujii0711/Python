"""6단계: RAG 체인 (검색 + 생성).

앞 단계까지가 '검색', 여기서 '생성'을 붙여 RAG 를 완성한다.
LCEL(파이프 연산자)로 이렇게 연결된다.

    질문 → Retriever → 검색된 청크를 문자열로 → 프롬프트 → LLM → 답변

로컬 모델을 transformers 파이프라인으로 돌린다. 기본값은 CPU 에서도 도는
작은 모델(Qwen2.5-0.5B-Instruct)이고, RAG_LLM 환경변수로 바꿀 수 있다.

먼저 04_index.py 를 실행해 두어야 한다.
"""

from pathlib import Path

from _config import (
    COLLECTION,
    LLM_MODEL,
    format_docs,
    get_client,
    get_device,
    get_torch_dtype,
    get_vector_store,
    run_hint,
    setup_console,
)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

QUESTIONS = [
    "파이썬 리스트를 원본 그대로 두고 뒤집으려면 어떻게 하나요?",
    "판다스에서 결측치를 채우는 방법을 알려줘",
    "Qdrant local 모드는 어떤 점을 조심해야 하나요?",
]

SYSTEM = (
    "너는 주어진 문서만 근거로 답하는 한국어 assistant 다.\n"
    "규칙:\n"
    "1. 문서에 없는 내용은 만들지 말고 '문서에서 찾을 수 없습니다' 라고 답한다.\n"
    "2. 3문장 이내로 간결하게 답한다.\n"
    "3. 근거로 쓴 문서 번호를 [1] 처럼 끝에 표시한다."
)

PROMPT = ChatPromptTemplate.from_messages(
    [("system", SYSTEM), ("human", "문서:\n{context}\n\n질문: {question}")]
)


def get_llm() -> ChatHuggingFace:
    """로컬 transformers 파이프라인을 LangChain 채팅 모델로 감싼다.

    HuggingFacePipeline.from_model_id 는 device 를 CUDA 인덱스 정수로만 받아서
    mps 를 지정할 수 없다. 그래서 파이프라인을 직접 만들어 넘긴다.
    """
    device = get_device()
    tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        LLM_MODEL,
        dtype=get_torch_dtype(),
    ).to(device)

    text_generation = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=256,
        do_sample=False,  # 근거 기반 답변이라 매번 같은 결과가 나오게 둔다
        return_full_text=False,  # 프롬프트는 되돌려주지 않고 생성분만
    )

    # ChatHuggingFace 가 모델의 chat template 을 적용해 준다.
    return ChatHuggingFace(
        llm=HuggingFacePipeline(pipeline=text_generation, model_id=LLM_MODEL),
        tokenizer=tokenizer,
    )


def build_chain(retriever, llm):
    """LCEL 체인. context 와 question 을 만들어 프롬프트에 넣고 LLM 에 넘긴다."""
    return (
        RunnableParallel(
            context=retriever | format_docs,
            question=RunnablePassthrough(),
        )
        | PROMPT
        | llm
        | StrOutputParser()
    )


if __name__ == "__main__":
    setup_console()

    client = get_client()
    if not client.collection_exists(COLLECTION):
        raise SystemExit(
            f"컬렉션이 없습니다. 먼저 `{run_hint('04_index.py')}` 를 실행하세요."
        )

    retriever = get_vector_store(client).as_retriever(search_kwargs={"k": 3})
    print(f"llm={LLM_MODEL} device={get_device()} (첫 실행은 모델 다운로드로 오래 걸립니다)")
    chain = build_chain(retriever, get_llm())

    for question in QUESTIONS:
        print(f"\n{'=' * 70}\n[질문] {question}")

        # 어떤 청크가 근거로 들어갔는지 눈으로 확인한다.
        docs = retriever.invoke(question)
        print("[검색된 근거]")
        for i, doc in enumerate(docs, start=1):
            source = Path(doc.metadata.get("source", "?")).name
            preview = doc.page_content[:60].replace("\n", " ")
            print(f"  [{i}] {source}: {preview}...")

        print(f"[답변]\n{chain.invoke(question).strip()}")

    client.close()
