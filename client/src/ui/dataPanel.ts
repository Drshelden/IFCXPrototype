import type { AppState, Instance, DataTab } from '../types';
import { selectTreeItem } from './tree';

let state: AppState;

export function initDataPanel(appState: AppState): void {
  state = appState;
}

function isGuid(value: unknown): value is string {
  const guidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return typeof value === 'string' && guidPattern.test(value);
}

function makeValueClickable(value: string): string {
  if (isGuid(value)) {
    return `<span class="data-guid-link" data-guid="${value}">${value}</span>`;
  }
  return value;
}

function formatValueForDisplay(value: unknown): string {
  if (typeof value === 'string') {
    try {
      const parsed = JSON.parse(value);
      if (typeof parsed === 'object' && parsed !== null) {
        return JSON.stringify(parsed, null, 2);
      }
    } catch {
      // not JSON, fall through
    }
    return value;
  }
  if (typeof value === 'object') {
    return JSON.stringify(value, null, 2);
  }
  return String(value);
}

function handleGuidLinkClick(e: Event): void {
  const target = e.target as HTMLElement;
  if (!target.classList.contains('data-guid-link')) return;
  e.preventDefault();
  const guid = target.dataset.guid;
  if (!guid) return;

  const componentItem = document.querySelector(`.tree-item[data-type="component"][data-guid="${CSS.escape(guid)}"]`);
  if (componentItem) {
    selectTreeItem('component', guid);
    renderDataViewForComponent(guid);
    return;
  }

  const entityItem = document.querySelector(`.tree-item[data-type="entity"][data-guid="${CSS.escape(guid)}"]`);
  if (entityItem) {
    selectTreeItem('entity', guid);
    renderDataViewForEntity(guid);
  }
}

export function clearDataView(): void {
  document.getElementById('dataHeaderText')!.textContent = 'Component Data';
  document.getElementById('dataStatus')!.textContent = '';
  document.getElementById('dataTabs')!.innerHTML = '';
  document.getElementById('dataView')!.innerHTML =
    '<div class="empty-state">Select an entity or component to inspect data</div>';
  state.dataTabs = [];
  state.activeTabId = null;
}

function summarizeKeyState(activeInstance: Instance, allInstances: Instance[]) {
  const stats = new Map<string, { presentCount: number; values: Set<string> }>();

  allInstances.forEach((instance) => {
    Object.entries(instance.component).forEach(([key, value]) => {
      if (!stats.has(key)) stats.set(key, { presentCount: 0, values: new Set() });
      const entry = stats.get(key)!;
      entry.presentCount += 1;
      entry.values.add(JSON.stringify(value));
    });
  });

  const rows: { key: string; value: unknown; stateClass: string }[] = [];
  Object.entries(activeInstance.component).forEach(([key, value]) => {
    const entry = stats.get(key) || { presentCount: 1, values: new Set([JSON.stringify(value)]) };
    let stateClass = 'row-unique';
    if (entry.presentCount > 1 && entry.values.size === 1) stateClass = 'row-overlap';
    if (entry.values.size > 1) stateClass = 'row-conflict';
    rows.push({ key, value, stateClass });
  });

  rows.sort((a, b) => a.key.localeCompare(b.key));
  return rows;
}

function renderDataTable(activeInstance: Instance, allInstances: Instance[]): void {
  const rows = summarizeKeyState(activeInstance, allInstances);
  const dataView = document.getElementById('dataView')!;
  if (!rows.length) {
    dataView.innerHTML = '<div class="empty-state">No scalar data available</div>';
    return;
  }

  const htmlRows = rows
    .map((row) => {
      const formattedValue = formatValueForDisplay(row.value);
      const escapedValue = (formattedValue || '').replace(/</g, '&lt;').replace(/>/g, '&gt;');
      const isMultiline = escapedValue.includes('\n');
      const cellContent = isMultiline ? `<pre>${escapedValue}</pre>` : makeValueClickable(escapedValue);
      return `<tr class="${row.stateClass}"><td>${row.key}</td><td>${cellContent}</td></tr>`;
    })
    .join('');

  dataView.innerHTML = `
    <table>
      <thead><tr><th>Key</th><th>Value</th></tr></thead>
      <tbody>${htmlRows}</tbody>
    </table>
  `;

  dataView.addEventListener('click', handleGuidLinkClick);

  const overlapCount = rows.filter((r) => r.stateClass === 'row-overlap').length;
  const uniqueCount = rows.filter((r) => r.stateClass === 'row-unique').length;
  const conflictCount = rows.filter((r) => r.stateClass === 'row-conflict').length;
  document.getElementById('dataStatus')!.textContent = `same:${overlapCount} unique:${uniqueCount} conflict:${conflictCount}`;
}

function renderDataTabs(instances: Instance[], headerLabel: string): void {
  const tabsEl = document.getElementById('dataTabs')!;
  tabsEl.innerHTML = '';
  state.dataTabs = instances.map(
    (instance): DataTab => ({
      tabId: instance.instanceId,
      label: `Q${(instance.queryIndex ?? (instance.component._query as number) ?? 0) + 1} · ${instance.modelName}`,
      instanceId: instance.instanceId,
    })
  );

  if (!state.dataTabs.length) {
    clearDataView();
    return;
  }

  if (!state.activeTabId || !state.dataTabs.some((tab) => tab.tabId === state.activeTabId)) {
    state.activeTabId = state.dataTabs[0].tabId;
  }

  document.getElementById('dataHeaderText')!.textContent = headerLabel;

  state.dataTabs.forEach((tab) => {
    const btn = document.createElement('button');
    btn.className = `data-tab${tab.tabId === state.activeTabId ? ' active' : ''}`;
    btn.textContent = tab.label;
    btn.addEventListener('click', () => {
      state.activeTabId = tab.tabId;
      renderDataTabs(instances, headerLabel);
      const activeInstance = state.flat.instancesById.get(tab.instanceId);
      if (activeInstance) {
        selectTreeItem('component', activeInstance.componentGuid, activeInstance.instanceId);
        renderDataTable(activeInstance, instances);
      }
    });
    tabsEl.appendChild(btn);
  });

  const active = state.flat.instancesById.get(state.activeTabId);
  if (active) renderDataTable(active, instances);
}

export function renderDataViewForComponent(componentGuid: string): void {
  const instanceIds = state.flat.componentsByGuid.get(componentGuid) || [];
  const instances = instanceIds.map((id) => state.flat.instancesById.get(id)).filter(Boolean) as Instance[];
  if (!instances.length) {
    clearDataView();
    return;
  }
  renderDataTabs(instances, `Component ${componentGuid}`);
}

export function renderDataViewForEntity(entityGuid: string): void {
  const entity = state.flat.entities.get(entityGuid);
  if (!entity) {
    clearDataView();
    return;
  }

  const firstComponentGuid = Array.from(entity.componentGuids.keys())[0];
  if (!firstComponentGuid) {
    clearDataView();
    return;
  }

  const instances = (entity.componentGuids.get(firstComponentGuid) || [])
    .map((id) => state.flat.instancesById.get(id))
    .filter(Boolean) as Instance[];

  if (!instances.length) {
    clearDataView();
    return;
  }

  renderDataTabs(instances, `Entity ${entityGuid}`);
}
