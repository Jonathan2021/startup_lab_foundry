'use strict';
(() => {
  const localToken = document.querySelector('meta[name="foundry-token"]').content;
  const newKey = () => crypto.randomUUID();
  const request = async (url, payload) => {
    const response = await fetch(url, payload === undefined ? {} : {
      method: 'POST', headers: {'Content-Type': 'application/json', 'X-Foundry-Token': localToken},
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (!response.ok) {
      const detail = result.error || (Array.isArray(result.detail) ? result.detail.map(e => e.msg).join('; ') : result.detail);
      throw new Error(detail || 'The operation could not be completed.');
    }
    return result;
  };
  const get = (form, name) => form.elements.namedItem(name)?.value?.trim() || '';
  const maybe = value => value || null;
  const entry = (parent, text, tag = 'p') => {
    const element = document.createElement(tag); element.textContent = text; parent.append(element); return element;
  };

  for (const form of document.querySelectorAll('form[data-lifecycle]')) {
    form.dataset.requestKey = newKey();
    let acceptedPreview = null;
    const acceptButton = form.querySelector('button[name="resolution"][value="accept"]');
    if (acceptButton) {
      acceptButton.disabled = true;
      form.addEventListener('input', () => {
        acceptedPreview = null; acceptButton.disabled = true;
        form.querySelector('.result-preview').replaceChildren();
      });
    }
    form.addEventListener('submit', async event => {
      event.preventDefault();
      const error = form.querySelector('.form-error'); error.textContent = '';
      const button = event.submitter || form.querySelector('button[type="submit"]');
      const original = button.textContent;
      const base = {request_key: form.dataset.requestKey, actor: get(form, 'actor')};
      let payload;
      if (form.dataset.lifecycle === 'context') {
        payload = {...base, work_id: get(form, 'work_id'), expected_work_version: Number(get(form, 'expected_work_version')),
          expected_head: get(form, 'expected_head'), evidence_ids: [...new FormData(form).getAll('evidence_id')],
          budget_bytes: 100000};
      } else if (form.dataset.lifecycle === 'capture') {
        payload = {...base, summary: get(form, 'summary'), details: get(form, 'details'), kind: get(form, 'kind'),
          epistemic_status: get(form, 'epistemic_status'), confidence: get(form, 'confidence'),
          sources: get(form, 'source') ? [get(form, 'source')] : []};
      } else if (form.dataset.lifecycle === 'work') {
        payload = {...base, expected_head: maybe(get(form, 'expected_head')), rationale: get(form, 'rationale'), work: {
          title: get(form, 'title'), description: get(form, 'description'), acceptance_criteria: get(form, 'acceptance_criteria'),
          kind: get(form, 'kind'), owner: get(form, 'owner'), status: 'ready'}};
      } else if (form.dataset.lifecycle === 'result') {
        payload = {...base, context_id: get(form, 'context_id'), summary: get(form, 'summary'), rationale: get(form, 'rationale'),
          limits: get(form, 'limits'), outcome: get(form, 'outcome'), decision_scope: get(form, 'decision_scope'),
          next_action: get(form, 'next_action'), revisit_trigger: maybe(get(form, 'revisit_trigger')),
          narrowed_objective: maybe(get(form, 'narrowed_objective')), chosen_branch: maybe(get(form, 'chosen_branch')),
          supersedes_result_id: maybe(get(form, 'supersedes_result_id')), reconciliation_rationale: maybe(get(form, 'reconciliation_rationale')),
          findings: get(form, 'finding_summary') ? [{summary: get(form, 'finding_summary'),
            sources: get(form, 'finding_source') ? [get(form, 'finding_source')] : [], epistemic_status: get(form, 'finding_status')}] : [],
          next_work: get(form, 'next_title') ? {title: get(form, 'next_title'), description: get(form, 'next_description'),
            acceptance_criteria: get(form, 'next_criteria'), owner: get(form, 'next_owner')} : null};
      } else if (form.dataset.lifecycle === 'resolve') {
        payload = {actor: base.actor, rationale: get(form, 'rationale'), resolution: button.value === 'preview' ? 'accept' : button.value,
          expected_result_digest: get(form, 'expected_result_digest'), expected_head: get(form, 'expected_head'),
          expected_work_version: Number(get(form, 'expected_work_version')), expected_review_revision: Number(get(form, 'expected_review_revision')),
          coverage_action: form.elements.namedItem('accept_limitation')?.checked ? 'accept_limitation' : null,
          coverage_rationale: maybe(get(form, 'coverage_rationale'))};
      }
      if (!payload) return;
      if (acceptButton && button.value === 'accept' && acceptedPreview !== JSON.stringify(payload)) {
        error.textContent = 'Preview these work effects before accepting.'; return;
      }
      button.disabled = true; button.textContent = 'Saving…';
      try {
        const previewing = button.value === 'preview';
        const result = await request(previewing ? form.dataset.endpoint.replace(/resolve$/, 'preview') : form.dataset.endpoint, payload);
        if (previewing) {
          const target = form.querySelector('.result-preview'); target.replaceChildren();
          entry(target, 'Preview only — no changes saved.', 'h3');
          entry(target, result.effects.completed_work_id ? 'This task will be completed.' : 'This task stays active.');
          entry(target, result.effects.next_work_id ? 'The proposed next task will be created.' : 'No next task will be created.');
          const affected = result.effects.work_needing_review || {};
          entry(target, Object.keys(affected).length + ' other tasks require review after these changes.');
          for (const [id, reasons] of Object.entries(affected)) entry(target, id + ': ' + JSON.stringify(reasons));
          acceptedPreview = JSON.stringify(payload); acceptButton.disabled = false;
          button.disabled = false; button.textContent = original;
        } else if (payload.resolution === 'defer') {
          location.reload();
        } else if (form.hasAttribute('data-reload')) location.reload();
        else location.assign(form.dataset.next + encodeURIComponent(result.id));
      } catch (failure) {
        error.textContent = failure.message || 'The server could not be reached. Retry unchanged after checking the connection.';
        button.disabled = false; button.textContent = original;
      }
    });
  }

  for (const button of document.querySelectorAll('[data-copy-context]')) button.addEventListener('click', async () => {
    const status = button.closest('section').querySelector('.copy-status');
    try {
      const data = await request('/api/contexts/' + encodeURIComponent(button.dataset.copyContext));
      await navigator.clipboard.writeText(data.markdown);
      status.textContent = 'Context copied. Give it to your agent; no worker was started.';
    } catch { status.textContent = 'Clipboard unavailable. Use Download Markdown.'; }
  });
  for (const button of document.querySelectorAll('[data-fetch-record]')) button.addEventListener('click', async () => {
    const target = button.nextElementSibling; target.replaceChildren();
    try {
      const data = await request('/api/contexts/' + encodeURIComponent(button.dataset.fetchContext) + '/records/evidence/' + encodeURIComponent(button.dataset.fetchRecord));
      entry(target, data.record.summary, 'h4'); entry(target, data.record.details || 'No further details');
      entry(target, data.record.confidence + ' confidence');
      if (!data.as_of_context) entry(target, 'Current record. Include it in a new context before relying on it for changes.');
    } catch (failure) { entry(target, failure.message); }
  });

  for (const form of document.querySelectorAll('[data-map-editor]')) {
    let approvedPreview = null;
    const key = newKey();
    const nodeContainer = form.querySelector('[data-map-nodes]');
    const edgeContainer = form.querySelector('[data-map-edges]');
    const error = form.querySelector('.form-error');
    const preview = form.querySelector('.map-preview');
    const nodes = () => [...nodeContainer.querySelectorAll('[data-map-node]')];
    const value = (field, name) => field.querySelector('[name="' + name + '"]')?.value?.trim() || '';
    const updateChoices = () => {
      for (const node of nodes()) {
        const control = node.querySelector('[name="node_ref"]');
        const record = value(node, 'node_kind') === 'record';
        node.querySelector('[data-node-reference]').hidden = !record; control.required = record;
      }
      for (const select of edgeContainer.querySelectorAll('[name="edge_source"],[name="edge_target"]')) {
        const previous = select.value || select.dataset.saved;
        select.replaceChildren(new Option('Choose a node', ''));
        for (const node of nodes()) select.add(new Option(value(node, 'node_title') || 'Untitled node', value(node, 'node_id')));
        select.value = previous; select.required = true; delete select.dataset.saved;
      }
    };
    const invalidate = () => { approvedPreview = null; preview.hidden = true; };
    form.addEventListener('input', event => {
      invalidate();
      if (event.target.name === 'node_title') updateChoices();
    });
    form.addEventListener('change', () => { invalidate(); updateChoices(); });
    form.querySelector('[data-map-add-node]').addEventListener('click', () => {
      const fragment = document.getElementById('map-node-template').content.cloneNode(true);
      fragment.querySelector('[name="node_id"]').value = 'node_' + newKey().replaceAll('-', '');
      nodeContainer.append(fragment); invalidate(); updateChoices();
      nodeContainer.lastElementChild.querySelector('[name="node_title"]').focus();
    });
    form.querySelector('[data-map-add-edge]').addEventListener('click', () => {
      edgeContainer.append(document.getElementById('map-edge-template').content.cloneNode(true));
      invalidate(); updateChoices(); edgeContainer.lastElementChild.querySelector('select').focus();
    });
    form.addEventListener('click', event => {
      if (event.target.closest('[data-map-remove]')) {
        event.target.closest('fieldset').remove(); invalidate(); updateChoices();
      }
    });
    form.querySelector('[data-record-search]').addEventListener('click', async () => {
      const target = form.querySelector('[data-record-results]'); target.replaceChildren();
      try {
        const kind = form.querySelector('[data-record-kind]').value;
        const q = form.querySelector('[data-record-query]').value;
        const data = await request('/api/workspaces/' + encodeURIComponent(form.dataset.workspace) + '/decision-records?' + new URLSearchParams({kind, q}));
        entry(target, data.items.length + ' of ' + data.total + ' matches. Refine the search if needed.');
        for (const row of data.items) {
          const code = row.kind + ':' + row.id;
          entry(target, row.label); entry(target, code, 'code');
          const option = document.createElement('option'); option.value = code; option.textContent = row.label;
          form.querySelector('datalist').append(option);
        }
      } catch (failure) { entry(target, failure.message); }
    });
    const serialize = () => ({
      expected_head: maybe(get(form, 'expected_head')), request_key: key, actor: get(form, 'actor'), rationale: get(form, 'rationale'),
      map: {
        nodes: nodes().map(node => {
          const reference = value(node, 'node_ref'); const split = reference.indexOf(':');
          return {id: value(node, 'node_id'), kind: value(node, 'node_kind'), title: value(node, 'node_title'), detail: value(node, 'node_detail'),
            ref: value(node, 'node_kind') === 'record' ? {kind: reference.slice(0, split), id: reference.slice(split + 1)} : null};
        }),
        edges: [...edgeContainer.querySelectorAll('[data-map-edge]')].map(edge => ({source: value(edge, 'edge_source'), target: value(edge, 'edge_target'),
          kind: value(edge, 'edge_kind'), condition: value(edge, 'edge_condition'), outcome: maybe(value(edge, 'edge_outcome'))})),
        focus: nodes().filter(node => node.querySelector('[name="node_focus"]').checked).map(node => value(node, 'node_id')),
      },
      work_treatments: [...form.querySelectorAll('[data-work-treatment]')].filter(field => value(field, 'treatment_action')).map(field => ({
        work_id: value(field, 'treatment_work_id'), expected_version: Number(value(field, 'treatment_version')), action: value(field, 'treatment_action'),
        rationale: value(field, 'treatment_rationale'), title: maybe(value(field, 'treatment_title')), description: maybe(value(field, 'treatment_description')),
      })),
    });
    form.addEventListener('submit', async event => {
      event.preventDefault(); error.textContent = ''; const button = event.submitter; button.disabled = true;
      try {
        const payload = serialize(); const result = await request(form.dataset.endpoint + '/preview', payload);
        const content = preview.querySelector('[data-preview-content]'); content.replaceChildren();
        entry(content, 'Save revision ' + result.sequence + ' with ' + payload.map.nodes.length + ' nodes. No future branch starts work.');
        const pending = Object.entries(result.needs_review);
        if (pending.length) {
          entry(content, 'These tasks will require review before execution:', 'strong');
          for (const [id, reason] of pending) {
            const node = payload.map.nodes.find(n => n.ref?.kind === 'work' && n.ref.id === id);
            entry(content, (node?.title || id) + ': ' + reason);
          }
        } else entry(content, 'No unresolved dependent-work review remains in this revision.');
        for (const treatment of payload.work_treatments) entry(content, treatment.action + ' ' + treatment.work_id + ': ' + treatment.rationale);
        approvedPreview = payload; preview.hidden = false;
      } catch (failure) { error.textContent = failure.message; }
      finally { button.disabled = false; }
    });
    form.querySelector('[data-map-apply]').addEventListener('click', async event => {
      if (!approvedPreview) return;
      const button = event.currentTarget; button.disabled = true; error.textContent = '';
      try { await request(form.dataset.endpoint, approvedPreview); location.assign(location.pathname + location.search); }
      catch (failure) { error.textContent = failure.message; button.disabled = false; }
    });
    updateChoices();
  }

  for (const graph of document.querySelectorAll('[data-decision-graph]')) {
    const data = JSON.parse(graph.dataset.map); const svg = graph.querySelector('svg');
    const cards = new Map([...graph.querySelectorAll('[data-node-id]')].map(card => [card.dataset.nodeId, card]));
    for (const node of data.nodes) if (cards.has(node.id)) cards.get(node.id).dataset.nodeKind = node.kind;
    const draw = () => {
      const bounds = graph.getBoundingClientRect();
      svg.setAttribute('viewBox', '0 0 ' + bounds.width + ' ' + bounds.height);
      svg.replaceChildren();
      for (const edge of data.edges) {
        const source = cards.get(edge.source), target = cards.get(edge.target); if (!source || !target) continue;
        const a = source.getBoundingClientRect(), b = target.getBoundingClientRect();
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        const x1 = a.left + a.width / 2 - bounds.left, y1 = a.top + a.height / 2 - bounds.top;
        const x2 = b.left + b.width / 2 - bounds.left, y2 = b.top + b.height / 2 - bounds.top;
        line.setAttribute('d', `M ${x1} ${y1} L ${x2} ${y2}`); line.setAttribute('class', edge.kind === 'may_lead_to' ? 'conditional' : 'relationship'); svg.append(line);
      }
    };
    new ResizeObserver(draw).observe(graph); draw();
    for (const card of cards.values()) card.addEventListener('click', () => {
      const detail = document.getElementById('node-' + card.dataset.nodeId); if (detail) detail.open = true;
    });
  }
})();
