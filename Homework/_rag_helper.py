INSTRUCTIONS = """
Your task is to answer questions from the course participants
based on the provided context.

Use the context to find relevant information and provide accurate
answers. If the answer is not found in the context,
respond with "I don't know."
"""

USER_PROMPT_TEMPLATE = """
QUESTION: {question}

CONTEXT:
{context}
""".strip()

class RAGBase:
    def __init__(
        self, 
        index,
        llm_client = 'openai_client',
        course = 'llm-zoomcamp',
        instructions = INSTRUCTIONS,
        prompt_template = USER_PROMPT_TEMPLATE,
        model = 'gpt-5.4-mini',
        input = 'qa'
    ):
        self.index = index
        self.llm_client = llm_client
        self.course = course
        self.instructions = instructions
        self.prompt_template = prompt_template
        self.model = model
        self.input = input

    def search(self, query, num_results=5):
        # boost_dict = {"question": 3.0, "section": 0.5}
        # filter_dict = {"course": self.course}

        return self.index.search(
            query,
            num_results=num_results
            # ,boost_dict=boost_dict,
            # filter_dict=filter_dict
        )

    def build_context_qa(self, search_results):
        lines = []

        for doc in search_results:
            lines.append(doc["question"])
            lines.append(doc["answer"])
            lines.append("")

        return "\n".join(lines).strip()

    def build_context_files(self, search_results):
        lines = []

        for doc in search_results:
            lines.append(doc["filename"])
            lines.append(doc["content"])
            lines.append("")

        return "\n".join(lines).strip()

    def build_prompt_qa(self, query, search_results):
        context = self.build_context_qa(search_results)
        return self.prompt_template.format(
            question=query,
            context=context
        )

    def build_prompt_files(self, query, search_results):
        context = self.build_context_files(search_results)
        return self.prompt_template.format(
            question=query,
            context=context
        )

    def llm(self, prompt):
        input_messages = [
            {"role": "developer", "content": self.instructions},
            {"role": "user", "content": prompt}
        ]

        response = self.llm_client.responses.create(
            model=self.model,
            input=input_messages
        )

        self.usage = response.usage
        self.input_tokens = self.usage.input_tokens
        self.output_tokens = self.usage.output_tokens
        return response.output_text

    def rag(self, query):
        search_results = self.search(query)
        if self.input == 'qa':
            prompt = self.build_prompt_qa(query, search_results)
        elif self.input == 'files':
            prompt = self.build_prompt_files(query, search_results)
        answer = self.llm(prompt)
        print(f'Usage: Input: {self.input_tokens}. Output: {self.output_tokens}.\n')
        return answer