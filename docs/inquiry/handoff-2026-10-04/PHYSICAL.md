# Physical-task public-data screen r1

PHYSICAL-20261004-001 uses the three-source stop rule in [PROTOCOL.md](PROTOCOL.md).
R002 supplies renovation experiences and potential contacts, not correctness labels.
This screen asks whether public data can substitute for expert-labeled examples of
observable renovation work. Documentation was inspected; no videos, models or
training data were downloaded and no benchmark was run.

| Source | Task / modality / labels | License and failure coverage | Fit for this investigation |
|---|---|---|---|
| CaptainCook4D | Egocentric multimodal cooking recordings with step/action annotations and induced recipe errors | Project specifies Apache 2.0; examples distinguish measurement, order, preparation and technique errors | Suitable for a cooking research question, not expert correctness of insulation, wiring, structural work or solar/heat-pump installation |
| Assembly101 mistake detection | Multiview toy assembly; timestamps, attach/detach, objects, mistake/correction labels | Official repo states CC BY-NC 4.0; example annotations include wrong order/position and unnecessary detach | Actual mistake labels exist; toy assembly and noncommercial restrictions do not establish field renovation suitability |
| Ego-Exo4D | Ego/exo skilled activity, including bike repair; expert commentary and proficiency benchmarks | Signed dataset licenses/access required; not obtained. Coverage is skill commentary/proficiency, not inspected renovation correctness labels | Relevant adjacent task/annotation concepts; no verified domain-matched failure split for these jobs |

Primary sources, checked 2026-10-04: [CaptainCook4D project](https://captaincook4d.github.io/captain-cook/),
[Assembly101 mistake annotations](https://github.com/assembly-101/assembly101-mistake-detection),
[Ego-Exo4D project and access terms](https://ego-exo4d-data.org/).
The first Assembly101 URL in the planning shortlist used the wrong organization;
corrected to `assembly-101` and retained the failed URL as an access attempt.

Assessment: labeled procedural mistakes are available publicly, so “no data exists”
is contradicted. These three sources do **not** substitute for labels covering the
reported renovation jobs, hidden defects or costly misses. No safety-critical
verification or benchmark accuracy is claimed. A synthetic toy benchmark would
test software and could not close this gate; it is not a prerequisite for current
Foundry operation, and local-model downloads/training remain deferred.

Decision: retain **expert/field-data hold** for that scope. The smallest useful input
is one repeatable low-risk observable step, permitted before/after examples, and a
competent labeler who can identify one expensive failure that looks correct. The
optional five-question ten-minute review is [R008](../../../requests/2026-10-04-followups.md).
Homeowner recollection remains useful problem evidence, separately from expert
labels. Do not extend this dataset hunt indefinitely or drop N001 merely because
construction ground truth is unavailable.
