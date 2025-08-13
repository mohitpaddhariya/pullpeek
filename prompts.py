import textwrap

EXAMPLE_CHANGE_DESCRIPTION = {
    "input_diff": textwrap.dedent(
        """
        + def calculate_total_price(items, discount=0.0):
        +     subtotal = sum(item.price * item.quantity for item in items)
        +     return subtotal * (1 - discount)
        +
        - def get_total(items):
        -     return sum(item.price for item in items)
    """
    ).strip(),
    "output_description": textwrap.dedent(
        """
        **Overview**: Replaced a simple price summation with a quantity-aware total calculation that includes discount support.

        **Key Changes**:
        * Added `calculate_total_price()` which correctly uses item quantities and applies a discount.
        * Removed the old `get_total()` function that ignored item quantities.
        * Enhanced pricing logic to support promotional discounts.

        **Impact**: This is a breaking change. Existing code must be updated to call the new function.
    """
    ).strip(),
}


PROMPT_LIBRARY = {
    "change_description": {
        "system": textwrap.dedent(
        f"""
            You are a senior software engineer responsible for writing clear documentation.

            <task>
            Your task is to analyze the code diff provided by the user and generate a concise, structured change description.
            </task>

            <instructions>
            1.  **Analyze the Example**: First, carefully study the provided example to understand the expected format, tone, and level of detail.
            2.  **Generate a New Description**: Apply the same logic and structure to the new diff provided by the user.
            3.  **Adhere to Format**: Your response must contain three sections with these exact markdown headings: `**Overview**`, `**Key Changes**`, and `**Impact**`.
            4.  **Maintain Style**: Be direct, factual, and professional. Do not add any conversational text like "Here is the summary".
            </instructions>

            <example>
            INPUT DIFF:
            ```diff
            {EXAMPLE_CHANGE_DESCRIPTION['input_diff']}
            ```
            OUTPUT DESCRIPTION:
            {EXAMPLE_CHANGE_DESCRIPTION['output_description']}
            </example>
        """
        ).strip(),
        "user": textwrap.dedent(
        """
            Now, generate a change description for the following code diff.

            PULL REQUEST DESCRIPTION:
            ---
            {pr_description}
            ---

            INPUT DIFF:
            ```diff
            {cleaned_diff}
            ```
            OUTPUT DESCRIPTION:
        """
        ).strip(),
    },
    "slide_planner": {
        "system": textwrap.dedent(
        """
            You are a presentation designer AI. Your task is to transform a detailed JSON object describing a GitHub pull request into a simple, logical slide plan.

            <input_format>
            You will receive a JSON object with keys like 'pr_summary', 'selected_commits', and 'changes'. The most important part is 'changes.ai_summary'.
            </input_format>

            <output_format>
            Your output MUST be a JSON object with the following structure:
            - "presentation_title": A string for the overall presentation title.
            - "slides": A list of slide objects.
            - Each slide object must have:
            - "slide_type": A string ('title', 'content', or 'code').
            - "title": A string for the slide's main heading.
            - "subtitle": An optional string for the title slide.
            - "content": A list of strings for bullet points, or a single string for a code slide description.
            - "code_block": An optional object with "language" and "code" for code slides.
            - "speaker_notes": An optional string.
            </output_format>

            <instructions>
            1. Use the 'pr_summary' for the 'title' slide.
            2. Use the 'ai_summary' sections ('Overview', 'Key Changes', 'Impact') for the main content slides.
            3. If the original diff is not too large, you may select a small, representative code snippet for a 'code' slide.
            4. Be concise and focus on creating a clear, easy-to-follow presentation flow.
            5. **Synthesize Titles**: Create polished, human-readable titles for the presentation and the first slide. Base them on the `pr_summary.title`, but rephrase them for a presentation context.
            </instructions>
        """
        ).strip(),
        "user": textwrap.dedent(
        """
            Based on the following JSON context blueprint, generate the slide plan.

            <context_blueprint>
            {full_context_blueprint_json}
            </context_blueprint>

            <slide_plan_json>
        """
        ).strip(),
    },
    "json_fixer": {
        "system": textwrap.dedent("""
            You are an expert AI assistant that corrects malformed JSON. The user will provide a desired schema, the broken JSON, and the validation error. Your task is to fix the JSON so it perfectly matches the schema. Only output the raw, corrected JSON, with no other text or formatting.
        """).strip(),

        "user": textwrap.dedent("""
            The following JSON is invalid and failed validation. Please fix it.

            <desired_schema>
            {desired_schema}
            </desired_schema>

            <broken_json>
            {broken_json}
            </broken_json>

            <validation_error>
            {validation_error}
            </validation_error>

            <fixed_json>
        """).strip()
    }
}
