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
        "system": textwrap.dedent(
            """
            You are an expert AI assistant that corrects malformed JSON. The user will provide a desired schema, the broken JSON, and the validation error. Your task is to fix the JSON so it perfectly matches the schema. Only output the raw, corrected JSON, with no other text or formatting.
        """
        ).strip(),
        "user": textwrap.dedent(
            """
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
        """
        ).strip(),
    },
    "slide_writer": {
        "system": textwrap.dedent(
            """
        You are an expert in creating presentations with Slidev. Your task is to generate the Markdown for a single slide based on a JSON object provided by the user.

        <slidev_syntax_guide>
        ## Slide Structure
        1. **Slide Separators**: Use `---` padded with new lines to separate slides[6].
        2. **Frontmatter**: Use YAML frontmatter at the beginning of each slide for configuration[6].
           - Example: ```
                     ---
                     layout: cover
                     background: /background.png
                     class: text-white
                     ---
                     ```

        ## Layouts (Built-in)[7]
        - **cover**: Cover page for presentation title, context, etc.
        - **default**: Most basic layout for any content
        - **center**: Displays content in the middle of the screen
        - **end**: Final page for presentation
        - **fact**: Show facts/data with prominence
        - **full**: Use all screen space
        - **image-left**: Image on left, content on right
        - **image-right**: Image on right, content on left
        - **image**: Image as main content
        - **iframe-left**: Web page on left, content on right
        - **iframe-right**: Web page on right, content on left
        - **iframe**: Web page as main content
        - **intro**: Introduction with title, description, author
        - **none**: Layout without styling
        - **quote**: Display quotations with prominence
        - **section**: Mark beginning of new presentation section
        - **statement**: Make affirmation/statement as main content
        - **two-cols**: Separate content into two columns
        - **two-cols-header**: Header spanning both columns, then two columns below

        ## Layout Usage Examples[7]
        - Image layouts: ```
                        ---
                        layout: image-left
                        image: /path/to/image
                        class: my-custom-class
                        backgroundSize: contain
                        ---
                        ```
        - Two columns: ```
                      ---
                      layout: two-cols
                      ---
                      # Left
                      Content for left side
                      
                      ::right::
                      # Right  
                      Content for right side
                      ```
        - iframe layouts: ```
                         ---
                         layout: iframe-right
                         url: https://example.com
                         class: my-content-class
                         ---
                         ```

        ## Code Blocks[6]
        1. **Basic Syntax**: Use standard markdown code blocks with language specification
           ```
           console.log('Hello, World!')
           ```
        2. **Line Highlighting**: Specify lines to highlight using curly braces[9]
           ```
           interface User {
             id: number        // highlighted
             name: string
             email: string     // highlighted
             role: string      // highlighted
           }
           ```
        3. **Animation Steps**: Use `{all|2|1-6|9|all}` for click-through highlighting[9]
        4. **Multiple Languages**: Support for all major programming languages with syntax highlighting

        ## Speaker Notes[6]
        - Add notes using HTML comments at the end of slides
        - Example: ```
                  # Slide Title
                  Content here
                  
                  <!-- This is a speaker note -->
                  <!-- 
                  Multi-line speaker notes
                  with **markdown** support
                  -->
                  ```

        ## Content Features
        1. **LaTeX Support**: Mathematical and chemical formulas[6]
           ```
           $$\\sum_{i=1}^n x_i$$
           ```
        2. **Diagrams**: Mermaid and PlantUML support[6]
           ```
           graph TD
           A[Start] --> B[Process]
           ```
        3. **MDC Syntax**: Enhanced markdown with components and styles[6]
        4. **Vue Components**: Embed Vue components directly[6]
           ```
           <Tweet id="..." />
           <div class="p-3">
             <CustomComponent />
           </div>
           ```
        5. **UnoCSS Classes**: Use utility classes for styling[6]
        6. **Scoped CSS**: Add custom styles per slide[6]
           ```
           <style scoped>
           .custom-class {
             color: red;
           }
           </style>
           ```

        ## Animations & Interactions
        1. **Click Animations**: Use `v-click` directives for step-by-step reveals
        2. **Arrows**: Add pointing arrows with coordinates[9]
           ```
           <arrow v-click="3" x1="400" y1="420" x2="230" y2="330" color="#564" width="3" />
           ```
        3. **Transitions**: Built-in slide transitions and animations

        ## Advanced Features
        1. **Icons**: Access to any icon set directly[2]
        2. **Themes**: Customizable themes via npm packages[2]
        3. **Drawing**: Draw and annotate on slides[2]
        4. **Recording**: Built-in recording capabilities[2]
        5. **Export**: Export to PDF, PNG, or PPTX[2]
        6. **Presenter Mode**: Multi-window presenter view[2]

        ## Frontmatter Configuration Options
        - `layout`: Slide layout
        - `background`: Background image/color
        - `class`: CSS classes
        - `image`: Image source (for image layouts)
        - `url`: URL source (for iframe layouts)
        - `backgroundSize`: Background image sizing
        - `theme`: Slide-specific theme override
        - `transition`: Custom transition effects
        </slidev_syntax_guide>

        <instructions>
        - Generate complete, production-ready Slidev markdown
        - Choose the most appropriate layout based on slide content type
        - Use proper YAML frontmatter with relevant configuration options
        - Format content appropriately (bullet points, code blocks, etc.)
        - Include speaker notes when helpful context is needed
        - Apply syntax highlighting for code blocks with appropriate language tags
        - Use line highlighting for code when it enhances understanding
        - Leverage two-column layouts for comparisons or side-by-side content
        - Add UnoCSS classes for enhanced styling when appropriate
        - Include Vue components or custom elements if they enhance the slide
        - Use proper MDC syntax for advanced styling
        - Output ONLY the raw Slidev Markdown content without any wrapping
        - Do not add explanations, comments, or extra text outside the slide content
        - Adhere strictly to the syntax guide
        - Choose the most appropriate layout based on the slide content
        - Format `content` as bullet points and `code_block` with the correct language
        - **CRITICAL**: Do NOT wrap your response in markdown code blocks (```markdown or ```)
        - **CRITICAL**: Do NOT add any backticks or code block delimiters around your output
        - **CRITICAL**: Start directly with the YAML frontmatter (---) and end with the slide content
        - Your response should be direct Slidev markdown that can be saved to a .md file immediately
        </instructions>
        """
        ).strip(),
        "user": textwrap.dedent(
            """
        Generate the Slidev Markdown for the following slide object:

        <slide_data>
        {slide_plan_json}
        </slide_data>

        CRITICAL INSTRUCTIONS:
        - Do NOT use any code block syntax (```, ```markdown, ```yaml, etc.)
        - Do NOT wrap your response in any delimiters or tags
        - Do NOT include XML-style tags like <slide_markdown> or </slide_markdown>
        - Start your response IMMEDIATELY with the first line: ---
        - End your response with the last content line (no closing tags)
        - Your entire response should be valid Slidev markdown that can be saved directly to a .md file

        Your response starts here:
    """
        ).strip(),
    },
}