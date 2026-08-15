import type { AppState, QueryLine } from '../types';
import { fetchJson, normalizeApiToComponents, normalizeQueryUrl } from '../api';
import { rebuildFlatState } from '../flatState';
import { renderTree, syncTreeCheckboxes } from './tree';
import { clearDataView } from './dataPanel';

export interface QueryLineCallbacks {
  onResultsChanged: (fromRepeat: boolean) => void;
  setStatus: (text: string, loading?: boolean) => void;
}

let state: AppState;
let callbacks: QueryLineCallbacks;

export function initQueryLines(appState: AppState, cb: QueryLineCallbacks): void {
  state = appState;
  callbacks = cb;
}

async function executeQueryLine(queryId: number, fromRepeat = false): Promise<void> {
  const line = state.queryLines.find((q) => q.id === queryId);
  if (!line) return;

  const rowEl = document.querySelector(`.query-line[data-id="${queryId}"]`);
  const statusEl = rowEl?.querySelector('.query-status') as HTMLElement | undefined;

  const inputUrl = line.address.trim();
  if (!inputUrl) return;
  const url = normalizeQueryUrl(inputUrl);

  if (statusEl) statusEl.textContent = 'Loading...';
  callbacks.setStatus(`Running query ${line.index + 1}`, true);

  try {
    const apiData = await fetchJson(url);
    const components = await normalizeApiToComponents(url, apiData);
    const withMeta = components.map((component) => ({ ...component, _query: line.index }));

    state.queryResults.set(queryId, withMeta);
    line.lastResultCount = withMeta.length;
    line.lastRunAt = new Date();

    if (statusEl) statusEl.textContent = `${withMeta.length} comps`;
    rebuildFlatState(state);
    renderTree();
    syncTreeCheckboxes();
    callbacks.onResultsChanged(fromRepeat);

    callbacks.setStatus(
      `Loaded ${state.flat.instancesById.size} component instances from ${state.queryResults.size} query line(s)`
    );
  } catch (error) {
    if (statusEl) statusEl.textContent = 'Error';
    callbacks.setStatus(`Error in query ${line.index + 1}: ${(error as Error).message}`);
  }
}

function stopRepeatTimer(line: QueryLine): void {
  if (!line?.repeatTimer) return;
  clearInterval(line.repeatTimer);
  line.repeatTimer = null;
}

function toggleQueryVisibility(queryId: number, show: boolean): void {
  state.flat.instancesById.forEach((instance) => {
    if (instance.queryId === queryId) {
      if (show) state.visibleInstanceIds.add(instance.instanceId);
      else state.visibleInstanceIds.delete(instance.instanceId);
    }
  });

  callbacks.onResultsChanged(true);
  syncTreeCheckboxes();
}

export function renderQueryLines(): void {
  const container = document.getElementById('queryLines')!;
  container.innerHTML = '';

  state.queryLines.forEach((line, index) => {
    line.index = index;
    const row = document.createElement('div');
    row.className = 'query-line';
    row.dataset.id = String(line.id);

    row.innerHTML = `
      <input class="query-input" value="${line.address.replace(/"/g, '&quot;')}" placeholder="Enter REST query URL or /api/...">
      <button class="icon-btn execute-btn" data-tooltip="Execute query">➜</button>
      <button class="icon-btn repeat-btn ${line.repeatEnabled ? 'active' : ''}" data-tooltip="Repeat every 1 minute">⟳</button>
      <button class="icon-btn show-btn" data-tooltip="Show all from this query">👁</button>
      <button class="icon-btn hide-btn" data-tooltip="Hide all from this query">🙈</button>
      <button class="icon-btn delete-btn" data-tooltip="Delete query line">✕</button>
      <span class="query-status">${line.lastResultCount ? `${line.lastResultCount} comps` : 'Idle'}</span>
    `;

    const input = row.querySelector('.query-input') as HTMLInputElement;
    const executeBtn = row.querySelector('.execute-btn')!;
    const repeatBtn = row.querySelector('.repeat-btn')!;
    const showBtn = row.querySelector('.show-btn')!;
    const hideBtn = row.querySelector('.hide-btn')!;
    const deleteBtn = row.querySelector('.delete-btn')!;

    input.addEventListener('input', (e) => (line.address = (e.target as HTMLInputElement).value));
    input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') executeQueryLine(line.id);
    });

    executeBtn.addEventListener('click', () => executeQueryLine(line.id));

    repeatBtn.addEventListener('click', () => {
      line.repeatEnabled = !line.repeatEnabled;
      repeatBtn.classList.toggle('active', line.repeatEnabled);
      if (line.repeatEnabled) {
        stopRepeatTimer(line);
        line.repeatTimer = setInterval(() => executeQueryLine(line.id, true), 60000);
        executeQueryLine(line.id, true);
      } else {
        stopRepeatTimer(line);
      }
    });

    showBtn.addEventListener('click', () => toggleQueryVisibility(line.id, true));
    hideBtn.addEventListener('click', () => toggleQueryVisibility(line.id, false));
    deleteBtn.addEventListener('click', () => deleteQueryLine(line.id));

    container.appendChild(row);
  });
}

export function addQueryLine(address = '/api/components', repeatEnabled = false): void {
  const line: QueryLine = {
    id: state.nextQueryId++,
    address,
    repeatEnabled,
    repeatTimer: null,
    lastResultCount: 0,
    lastRunAt: null,
    index: state.queryLines.length,
  };
  state.queryLines.push(line);
  renderQueryLines();

  if (repeatEnabled) {
    line.repeatTimer = setInterval(() => executeQueryLine(line.id, true), 60000);
  }
}

export function deleteQueryLine(queryId: number): void {
  const idx = state.queryLines.findIndex((q) => q.id === queryId);
  if (idx < 0) return;

  const [line] = state.queryLines.splice(idx, 1);
  stopRepeatTimer(line);
  state.queryResults.delete(queryId);

  if (!state.queryLines.length) {
    addQueryLine('/api/components');
  }

  rebuildFlatState(state);
  renderQueryLines();
  renderTree();
  syncTreeCheckboxes();
  callbacks.onResultsChanged(true);
  clearDataView();
}

export function saveQueryState(): void {
  const payload = {
    version: 1,
    savedAt: new Date().toISOString(),
    queries: state.queryLines.map((line) => ({ address: line.address, repeat: !!line.repeatEnabled })),
  };

  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'ifcx-query-state.json';
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
  callbacks.setStatus('Saved query state JSON');
}

export async function openQueryState(file: File): Promise<void> {
  const text = await file.text();
  const parsed = JSON.parse(text);
  if (!parsed || !Array.isArray(parsed.queries)) throw new Error('Invalid query state format');

  state.queryLines.forEach(stopRepeatTimer);
  state.queryLines = [];
  state.queryResults.clear();
  state.flat = { entities: new Map(), componentsByGuid: new Map(), instancesById: new Map() };
  state.visibleInstanceIds.clear();
  state.selectedInstanceId = null;

  parsed.queries.forEach((query: { address?: string; repeat?: boolean }) =>
    addQueryLine(query.address || '', !!query.repeat)
  );
  if (!state.queryLines.length) addQueryLine('/api/components');

  renderQueryLines();
  renderTree();
  clearDataView();
  callbacks.setStatus('Loaded query state JSON');
}
