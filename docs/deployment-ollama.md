# Local Ollama example

This portfolio-only document shows the local inference boundary. It is a
sanitized design example, not a runnable application setup. Model weights,
secrets, and machine-specific paths are intentionally omitted.

## Configuration pattern

The provider and model are selected per agent through environment variables:

```env
OPTIONAI_LLM_PROVIDER=google
OPTIONAI_TECHNICAL_LLM_PROVIDER=ollama
OPTIONAI_TECHNICAL_LLM_MODEL=local-model-name
OPTIONAI_OLLAMA_BASE_URL=http://localhost:11434
```

An agent-specific value overrides the global provider/model. Other agents can
continue using Gemini. The local model is accessed through the model factory,
so agents do not depend directly on Ollama.

## Model formats and isolation

Ollama can serve named models and import compatible GGUF files, including
models obtained from Hugging Face. Large model weights should remain outside
the repository. A tracked `Modelfile` example may document how a local model is
created, but real paths belong only in an ignored local file.

The local API image may contain the Ollama client while the cloud API image can
omit local-only dependencies. Cloud Run uses hosted models in the current
design; local model weights are not deployed.

## Evaluation principle

Local models should be compared with the same frozen inputs, prompts, and
schemas as hosted models. Measure latency, structured-output validity, factual
grounding, neutrality, and usefulness—not only whether the model responds.
