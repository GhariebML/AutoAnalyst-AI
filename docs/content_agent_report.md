# AdPilot Content Agent Report

## Summary of Analysis

AdPilot Phase 1 is intentionally focused on establishing an autonomous marketing agent pipeline skeleton rather than delivering full AI behavior. The codebase defines:

- A clean package structure with `src/adpilot/` for agents, orchestration, prompts, schemas, services, and utilities.
- Shared Pydantic v2 schemas as the contract for every agent stage.
- A `ContentAgent` placeholder in `src/adpilot/agents/content_agent.py` with a `NotImplementedError` stub.
- A content system prompt template in `src/adpilot/prompts/content_system_prompt.md` that enforces JSON-only output and points to `ContentAgentInput` and `ContentAgentOutput`.

The content pipeline is designed to consume strategic and research outputs and produce marketing creative assets:

- `ContentAgentInput` includes `strategy: StrategyAgentOutput` and `research: ResearchAgentOutput`.
- `ContentAgentOutput` is expected to deliver:
  - ads (`AdCopy`)
  - email sequences (`EmailSequence`)
  - social posts (`SocialPost`)
  - blog outlines (`BlogOutline`)
  - CTA variants (`CTAVariant`)
  - a `content_calendar_note`

Current Phase 1 completeness for content:

- schema definitions exist and are validated
- prompt scaffolding exists
- agent class exists with metadata (`name`, `input_model`, `output_model`, `prompt_path`)
- no actual generation logic or external API integration is implemented

## Key Findings for Content Agent

1. `ContentAgent` is a placeholder only:
   - `async def run(...)` raises `NotImplementedError`
   - no logic for prompt construction, LLM invocation, or output parsing

2. Content schema coverage is strong:
   - supports funnel-aware ads, email sequences, social posts, blog outlines, CTAs
   - includes data validation rules such as hashtag normalization and funnel coverage checks

3. Prompt definition is minimal and needs expansion:
   - current prompt file only defines role, input/output schema, and JSON-only output rule
   - TODO remains to inject Pydantic schema from `ContentAgentOutput.model_json_schema()`

4. Phase 1 project scope clearly excludes real LLM and external service integration.

## Roadmap for `ContentAgent` Development (as Sleem, Content Agent Developer)

### Phase 2 implementation goals

1. Build the content generation flow
   - implement `ContentAgent.run()`
   - create prompt builder using `strategy` and `research` inputs
   - compose a clear system/user prompt with example structure and schema expectations

2. Integrate the LLM client
   - use `src/adpilot/services/llm_client.py` for model calls
   - ensure agent sends prompt and receives raw response safely
   - parse and validate JSON output against `ContentAgentOutput`

3. Enforce schema-driven output
   - embed `ContentAgentOutput.model_json_schema()` or equivalent schema guidance into the prompt
   - validate the returned JSON with the Pydantic model
   - add robust error handling for invalid or incomplete LLM responses

4. Cover creative output types
   - generate at least one asset per output category in a baseline implementation
   - ensure ads cover multiple funnel stages and channel formats
   - produce a realistic email sequence and social post variants
   - include blog outlines and CTA variants aligned with campaign strategy

5. Add tests for behavior and integration
   - unit tests for prompt generation and JSON schema validation
   - sample output fixture tests for `ContentAgentOutput`
   - error case tests for invalid model responses

6. Polish prompt and agent metadata
   - update `src/adpilot/prompts/content_system_prompt.md` with explicit schema injection guidance
   - keep `Return ONLY valid JSON` rule strict
   - document any fallback behavior if the LLM returns invalid output

### Suggested development milestones

- Milestone 1: implement `ContentAgent.run()` with placeholder prompt builder and model call stub
- Milestone 2: connect to `LLMClient` and parse JSON into `ContentAgentOutput`
- Milestone 3: validate schema adherence and add unit tests
- Milestone 4: expand content prompt to handle creative variety, funnel coverage, and brand tone
- Milestone 5: finalize documentation in `docs/` and ensure Phase 2 agent fits the AdPilot pipeline

---

## Quick Checklist for Sleem

- [ ] Implement `ContentAgent.run()` in `src/adpilot/agents/content_agent.py`
- [ ] Build prompt assembly logic using `strategy` and `research` input models
- [ ] Inject `ContentAgentOutput.model_json_schema()` or schema guidance into `src/adpilot/prompts/content_system_prompt.md`
- [ ] Use `src/adpilot/services/llm_client.py` to send prompts and receive responses
- [ ] Parse the LLM response into `ContentAgentOutput` and validate it
- [ ] Add tests for prompt generation, valid JSON parsing, and failure handling
- [ ] Update docs and comments to reflect the completed Phase 2 behavior

## Presentation-Style Roadmap

1. **Design**: define the content prompt structure and schema anchor.
2. **Implement**: add `ContentAgent.run()` and prompt builder.
3. **Integrate**: connect the agent to `LLMClient` and handle raw responses.
4. **Validate**: parse JSON into `ContentAgentOutput` and enforce schema rules.
5. **Test & document**: cover positive/negative flows and refresh `docs/`.

## Recommended next step

Start by implementing the content prompt builder and a strict JSON parser for `ContentAgentOutput`. That will unlock safe integration with the LLM client and make the content agent ready for Phase 2 end-to-end testing.
