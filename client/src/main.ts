import './style.css';
import { createInitialState } from './types';
import {
  initTree,
  renderTree,
  syncTreeCheckboxes,
  clearTreeAndSelection,
  selectTreeItem,
} from './ui/tree';
import { initDataPanel, renderDataViewForComponent, renderDataViewForEntity, clearDataView } from './ui/dataPanel';
import {
  initQueryLines,
  addQueryLine,
  saveQueryState,
  openQueryState,
} from './ui/queryLines';
import { setupSplitter, setupHorizontalSplitter } from './ui/splitters';
import { Viewer3D } from './viewer3d';

const state = createInitialState();

function setStatus(text: string, loading = false): void {
  const status = document.getElementById('statusText')!;
  status.innerHTML = loading ? `${text}<span class="loading"></span>` : text;
}

const viewer3d = new Viewer3D({
  iframe: document.getElementById('viewerFrame') as HTMLIFrameElement,
  modelSelect: document.getElementById('modelSelect') as HTMLSelectElement,
  resetButton: document.getElementById('resetViewBtn') as HTMLButtonElement,
  statusEl: document.getElementById('viewerStatus')!,
  onPicked: (entityGuid) => {
    if (!state.flat.entities.has(entityGuid)) return;
    selectTreeItem('entity', entityGuid);
    renderDataViewForEntity(entityGuid);
  },
});

function syncViewerVisibility(): void {
  const visible: string[] = [];
  const hidden: string[] = [];
  state.flat.entities.forEach((node, entityGuid) => {
    const instanceIds = Array.from(node.componentGuids.values()).flat();
    const isVisible = instanceIds.some((id) => state.visibleInstanceIds.has(id));
    (isVisible ? visible : hidden).push(entityGuid);
  });
  viewer3d.showEntities(visible);
  viewer3d.hideEntities(hidden);
}

initTree(state, {
  onVisibilityChange: syncViewerVisibility,
  onSelectEntity: (entityGuid) => {
    renderDataViewForEntity(entityGuid);
    viewer3d.highlightEntities([entityGuid]);
    viewer3d.flyToEntities([entityGuid]);
  },
  onSelectComponent: (componentGuid) => {
    renderDataViewForComponent(componentGuid);
    const instanceIds = state.flat.componentsByGuid.get(componentGuid) || [];
    const instance = instanceIds.map((id) => state.flat.instancesById.get(id)).find(Boolean);
    if (instance) {
      viewer3d.highlightEntities([instance.entityGuid]);
      viewer3d.flyToEntities([instance.entityGuid]);
    }
  },
  onClearSelection: () => {
    clearDataView();
  },
});

initDataPanel(state);

initQueryLines(state, {
  onResultsChanged: syncViewerVisibility,
  setStatus,
});

function setupMenuActions(): void {
  document.getElementById('addQueryBtn')!.addEventListener('click', () => addQueryLine('/api/components'));
  document.getElementById('saveQueriesBtn')!.addEventListener('click', saveQueryState);
  document.getElementById('openQueriesBtn')!.addEventListener('click', () => {
    (document.getElementById('openQueriesInput') as HTMLInputElement).click();
  });

  document.getElementById('openQueriesInput')!.addEventListener('change', async (e) => {
    const file = (e.target as HTMLInputElement).files?.[0];
    if (!file) return;
    try {
      await openQueryState(file);
    } catch (error) {
      setStatus(`Open failed: ${(error as Error).message}`);
    } finally {
      (e.target as HTMLInputElement).value = '';
    }
  });
}

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') {
    clearTreeAndSelection();
    clearDataView();
  }
});

window.addEventListener('load', () => {
  setupSplitter();
  setupHorizontalSplitter();
  setupMenuActions();
  void viewer3d.populateModelList();
  addQueryLine('/api/components');
  renderTree();
  syncTreeCheckboxes();
  clearDataView();
});
