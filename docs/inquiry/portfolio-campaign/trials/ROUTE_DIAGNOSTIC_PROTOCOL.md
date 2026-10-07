# T5d — diagnose the failed request format

Frozen after T5's six HTTP 500 responses and before diagnostic requests.
T5 remains inconclusive. Its first script failed to retain HTTP error bodies.

At most two additional requests, each capped at 30 seconds, using the same A→C
coordinates: repeat the `false` request while retaining its error body, then use
numeric `0` for the same profile parameter. The only changed variable is boolean
encoding. Record errors as artifacts. No tuning coordinates or route objective.

If the response identifies a formatting error and numeric encoding works, allow
one separately recorded T5r repeat (same six cases, numeric 0/1). Otherwise stop
this public-service arm. An access or harness failure is not a routing feature gap.
