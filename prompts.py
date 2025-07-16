import textwrap

EXAMPLE_CHANGE_DESCRIPTION = {
    "input_diff": textwrap.dedent("""
        + def calculate_total_price(items, discount=0.0):
        +     subtotal = sum(item.price * item.quantity for item in items)
        +     return subtotal * (1 - discount)
        +
        - def get_total(items):
        -     return sum(item.price for item in items)
    """).strip(),
    "output_description": textwrap.dedent("""
        **Overview**: Replaced a simple price summation with a quantity-aware total calculation that includes discount support.

        **Key Changes**:
        * Added `calculate_total_price()` which correctly uses item quantities and applies a discount.
        * Removed the old `get_total()` function that ignored item quantities.
        * Enhanced pricing logic to support promotional discounts.

        **Impact**: This is a breaking change. Existing code must be updated to call the new function.
    """).strip()
}


PROMPT_LIBRARY = {
    "change_description": {
        "system": textwrap.dedent(f"""
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
        """).strip(),

        "user": textwrap.dedent("""
            Now, generate a change description for the following code diff.

            INPUT DIFF:
            ```diff
            {cleaned_diff}
            ```
            OUTPUT DESCRIPTION:
        """).strip(),
    }
}