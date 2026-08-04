# Reproducibility contract

Published benchmark results should record:

- model repository and immutable revision
- tokenizer revision when different
- model license
- benchmark name/version/revision
- inference backend and version
- dtype/quantization
- prompt/chat template
- few-shot count
- decoding parameters
- seed when applicable
- hardware/platform
- normalized result JSON

Training artifacts should additionally record each source key/revision/license and derived-data manifest hash. This makes it possible to reconstruct which exact corpus produced a model and to investigate benchmark overlap later.
