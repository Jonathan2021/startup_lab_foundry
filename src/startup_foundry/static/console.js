'use strict';
function proposalPayload(values, payload) {
  const capabilities = values.getAll('scope_capability');
  payload.scope = capabilities.map((capability, i) => ({capability,
    treatment: values.getAll('scope_treatment')[i],
    provenance: values.getAll('scope_provenance')[i], reason: values.getAll('scope_reason')[i]}));
  payload.alternatives = values.getAll('alternative');
  payload.work_treatments = values.getAll('work_id').map((work_id, i) => ({work_id,
    treatment: values.getAll('work_treatment')[i], reason: values.getAll('work_reason')[i]}));
  for (const key of ['scope_capability','scope_treatment','scope_provenance','scope_reason','alternative','work_id','work_treatment','work_reason']) delete payload[key];
  return payload;
}
const token = document.querySelector('meta[name="foundry-token"]').content;
for (const form of document.querySelectorAll('form[data-api]')) {
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const button = form.querySelector('button[type="submit"]');
    const error = form.querySelector('.form-error');
    const values = new FormData(form);
    let payload = Object.fromEntries(values);
    if (form.hasAttribute('data-proposal-edit')) payload = proposalPayload(values, payload);
    for (const key of ['expected_sequence', 'expected_revision', 'expected_review_revision', 'expected_version', 'draft_revision']) {
      if (Object.hasOwn(payload, key)) payload[key] = Number(payload[key]);
    }
    if (Object.hasOwn(payload, 'next_work_item_id') && !payload.next_work_item_id) payload.next_work_item_id = null;
    if (Object.hasOwn(payload, 'expected_revision_id') && !payload.expected_revision_id) payload.expected_revision_id = null;
    for (const key of ['preview', 'changes', 'scope', 'alternatives']) {
      if (Object.hasOwn(payload, key) && typeof payload[key] === 'string') {
        try { payload[key] = JSON.parse(payload[key]); }
        catch { error.textContent = 'Invalid JSON in ' + key; return; }
      }
    }
    if (form.hasAttribute('data-score')) {
      payload.scores = {};
      for (const key of Object.keys(payload)) {
        if (key.startsWith('score:')) {
          payload.scores[key.slice(6)] = payload[key] === '' ? null : Number(payload[key]);
          delete payload[key];
        }
      }
    }
    if (form.hasAttribute('data-project')) {
      payload.repositories = payload.repository_reference ? [{local_reference:payload.repository_reference, observed_at:new Date().toISOString(), dirty_state:'unknown'}] : [];
      delete payload.repository_reference;
      for (const key of ['gaps','participants_as_reported','prior_decisions_constraints']) {
        payload[key] = payload[key].split('\n').map((x) => x.trim()).filter(Boolean);
      }
      if (!payload.source_idea_id) payload.source_idea_id = null;
    }
    if (form.hasAttribute('data-draft')) {
      const wrapper = form.hasAttribute('data-create') ? {venture_id:payload.venture_id,request_key:payload.request_key} : {expected_version:payload.expected_version,actor:payload.actor};
      for (const key of ['to','cc','bcc','source_evidence_ids']) payload[key] = payload[key].split(',').map((x) => x.trim()).filter(Boolean);
      payload.attachment_artifact_ids = values.getAll('attachment_artifact_ids');
      payload.related_request_id = payload.related_request_id || null;
      for (const key of ['venture_id','request_key','expected_version','actor']) delete payload[key];
      payload = {...wrapper, draft:payload};
    }
    if (form.hasAttribute('data-outcome')) payload.stated_at = new Date(payload.stated_at).toISOString();
    if (Object.hasOwn(payload, 'parent_ids')) {
      payload.parent_ids = payload.parent_ids.split(',').map((x) => x.trim()).filter(Boolean);
    }
    if (form.hasAttribute('data-config')) payload.modules=values.getAll('modules');
    if (form.hasAttribute('data-metrics')) for (const key of ['revenue','costs']) payload[key]=payload[key]===''?null:payload[key];
    if (payload.reconciliation === '') payload.reconciliation = null;
    const original = button.textContent;
    button.disabled = true;
    button.textContent = 'Working…';
    error.textContent = '';
    try {
      const response = await fetch(form.dataset.api, {
        method: 'POST', headers: {'Content-Type': 'application/json', 'X-Foundry-Token': token},
        body: JSON.stringify(payload),
      });
      const result = await response.json();
      if (!response.ok) {
        const detail = result.error || (Array.isArray(result.detail) ? result.detail.map((e) => e.msg).join('; ') : result.detail);
        throw new Error(detail || 'The request could not be completed.');
      }
      if (form.hasAttribute('data-reload')) location.reload();
      else if (form.dataset.redirectTemplate) location.assign(form.dataset.redirectTemplate.replace('{id}', encodeURIComponent(result.id)));
      else location.assign(form.dataset.redirect + encodeURIComponent(result.id));
    } catch (failure) {
      error.textContent = failure.message || 'The local server could not be reached.';
      button.disabled = false;
      button.textContent = original;
    }
  });
}

for (const button of document.querySelectorAll('[data-copy]')) button.addEventListener('click', async () => {try {await navigator.clipboard.writeText(button.dataset.copy); button.textContent='Copied';} catch {button.textContent=button.dataset.copy;}});
for (const select of document.querySelectorAll('[data-switch]')) select.addEventListener('change', () => location.assign(select.value));

for (const button of document.querySelectorAll('[data-copy-url]')) button.addEventListener('click', async () => {
  const status = document.querySelector('.copy-status');
  try {const response=await fetch(button.dataset.copyUrl); if(!response.ok) throw new Error('Cannot export handoff'); const data=await response.json(); await navigator.clipboard.writeText(JSON.stringify(data,null,2)); status.textContent='Handoff copied. Start an agent session explicitly to continue.';}
  catch {status.textContent='Clipboard unavailable. Use Download JSON to export the handoff.';}
});

for (const button of document.querySelectorAll('[data-add-row]')) button.addEventListener('click', () => {
  const template = document.getElementById(button.dataset.rowTemplate);
  const container = document.getElementById(button.dataset.addRow);
  container.append(template.content.cloneNode(true));
  container.lastElementChild.querySelector('input,textarea').focus();
});
document.addEventListener('click', (event) => {
  const button = event.target.closest('[data-remove-row]');
  if (button) button.closest('fieldset').remove();
});
