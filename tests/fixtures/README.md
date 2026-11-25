# Isolated timeout evidence fixture

`f2-review-timeout-test.bpmn` is a test-only copy of the assessed executable at the time of the 24 November live check. It has a distinct process ID, prefixed message/job types, latest form bindings, and a five-second review boundary instead of PT48H. It must not be uploaded as the assessed F2 model or included in normal F2 deployments. The deploy_f2.py helper explicitly selects only the two assessed BPMNs and three forms.

The test instance starts directly at Activity_07qa1zf with a nonexistent synthetic product ID; it exercises boundary cancellation and the timeout end event without inventory jobs. It does not prove a real 48-hour elapsed wait. Full live evidence and keys are in docs/f2-tasklist-live-validation-2026-11-24.md.

