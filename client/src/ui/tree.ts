import type { AppState, Component } from '../types';

export interface TreeCallbacks {
  onVisibilityChange: () => void;
  onSelectEntity: (entityGuid: string) => void;
  onSelectComponent: (componentGuid: string, instanceId?: string) => void;
  onClearSelection: () => void;
}

let state: AppState;
let callbacks: TreeCallbacks;

export function initTree(appState: AppState, cb: TreeCallbacks): void {
  state = appState;
  callbacks = cb;
}

function getComponentTypeInfo(component: Component | null) {
  if (!component) return { icon: '●', iconClass: 'component', displayName: 'Component' };

  const componentType = (component.componentType as string) || '';
  const componentName = (component.componentName as string) || '';

  if (componentType.startsWith('IfcRel') || componentType.includes('Relation')) {
    return { icon: '↔', iconClass: 'component-relation', displayName: 'Relation' };
  } else if (componentType.includes('PropertySet') || componentName.startsWith('Pset_')) {
    return {
      icon: '<span class="icon-grid-pset" aria-hidden="true"><i></i><i></i><i></i><i></i></span>',
      iconClass: 'component-pset',
      displayName: 'PropertySet',
    };
  } else if (componentType.includes('ShapeRepresentation')) {
    return { icon: '▲', iconClass: 'component-shape', displayName: 'ShapeRep' };
  }
  return { icon: '●', iconClass: 'component-classdata', displayName: 'ClassData' };
}

function createTreeItem(opts: {
  type: string;
  label: string;
  guid?: string;
  count?: number;
  leaf?: boolean;
  tooltip?: string;
  component?: Component | null;
}): HTMLDivElement {
  const { type, label, guid, count, leaf = false, tooltip = '', component = null } = opts;
  const item = document.createElement('div');
  item.className = `tree-item${leaf ? ' leaf' : ''}`;
  item.dataset.type = type;
  if (guid) item.dataset.guid = guid;

  let icon: string;
  let iconClass: string;
  let labelClass = '';

  if (type === 'entity') {
    icon = '⬡';
    iconClass = 'entity';
    labelClass = 'entity-name';
  } else if (type === 'component' && component) {
    const typeInfo = getComponentTypeInfo(component);
    icon = typeInfo.icon;
    iconClass = typeInfo.iconClass;
    labelClass = typeInfo.iconClass;
  } else {
    icon = type === 'component' ? '●' : '\u{1F4E6}';
    iconClass = type === 'component' ? 'component' : '';
  }

  item.innerHTML = `
    <div class="tree-item-content" title="${tooltip}">
      <span class="tree-toggle"></span>
      <input type="checkbox" class="tree-checkbox">
      <span class="tree-icon ${iconClass}">${icon}</span>
      <span class="tree-label ${labelClass}">${label}</span>
      <span class="tree-count">${count !== undefined ? `(${count})` : ''}</span>
    </div>
  `;
  return item;
}

function attachTreeSelectionHandlers(item: HTMLElement, onSelect: () => void): void {
  const toggle = item.querySelector('.tree-toggle');
  if (toggle) {
    toggle.addEventListener('click', (e) => {
      e.stopPropagation();
      if (!item.classList.contains('leaf')) item.classList.toggle('expanded');
    });
  }

  item.addEventListener('click', (e) => {
    if ((e.target as HTMLElement).closest('.tree-toggle, .tree-checkbox')) return;
    e.stopPropagation();
    if (!item.classList.contains('leaf')) item.classList.toggle('expanded');
    onSelect();
  });
}

export function cssEscape(value: string): string {
  if (window.CSS && CSS.escape) return CSS.escape(value);
  return String(value).replace(/([ #;?%&,.+*~':"!^$[\]()=>|/@])/g, '\\$1');
}

function expandToItem(item: HTMLElement): void {
  let current: HTMLElement | null = item;
  while (current && current.classList && current.classList.contains('tree-item')) {
    current.classList.add('expanded');
    current = current.parentElement ? current.parentElement.closest('.tree-item') : null;
  }
}

export function renderTree(): void {
  const container = document.getElementById('treeContainer')!;
  const treeCount = document.getElementById('treeCount')!;
  container.innerHTML = '';

  const entityCount = state.flat.entities.size;
  const componentCount = state.flat.instancesById.size;
  treeCount.textContent = `${entityCount} entities, ${componentCount} components`;

  if (!entityCount) {
    container.innerHTML = '<div class="empty-state">Execute a query line to load data</div>';
    return;
  }

  const rootItem = createTreeItem({
    type: 'root',
    label: 'IFCxPrototype',
    guid: 'IFCxPrototype',
    count: componentCount,
    tooltip: 'All entities and components from all query lines',
  });
  rootItem.classList.add('expanded');

  const rootChildren = document.createElement('div');
  rootChildren.className = 'tree-children';

  const sortedEntities = Array.from(state.flat.entities.values()).sort((a, b) =>
    a.entityGuid.localeCompare(b.entityGuid)
  );

  sortedEntities.forEach((entityNode) => {
    const componentGuidEntries = Array.from(entityNode.componentGuids.entries()).sort((a, b) =>
      a[0].localeCompare(b[0])
    );
    const entityItem = createTreeItem({
      type: 'entity',
      label: entityNode.entityGuid,
      guid: entityNode.entityGuid,
      count: componentGuidEntries.length,
      tooltip: `Entity ${entityNode.entityGuid} (${componentGuidEntries.length} component GUIDs)`,
    });
    entityItem.classList.add('expanded');

    const entityChildren = document.createElement('div');
    entityChildren.className = 'tree-children';

    componentGuidEntries.forEach(([componentGuid, instanceIds]) => {
      const firstInstance = state.flat.instancesById.get(instanceIds[0]);
      const component = firstInstance ? firstInstance.component : null;

      const componentItem = createTreeItem({
        type: 'component',
        label: componentGuid,
        guid: componentGuid,
        count: instanceIds.length,
        leaf: true,
        tooltip: `Component ${componentGuid} (${instanceIds.length} matching instances)`,
        component,
      });
      componentItem.dataset.instanceIds = JSON.stringify(instanceIds);

      const compCheckbox = componentItem.querySelector('.tree-checkbox') as HTMLInputElement;
      compCheckbox.checked = instanceIds.every((id) => state.visibleInstanceIds.has(id));
      compCheckbox.addEventListener('change', (e) => {
        if ((e.target as HTMLInputElement).checked) {
          instanceIds.forEach((id) => state.visibleInstanceIds.add(id));
        } else {
          instanceIds.forEach((id) => state.visibleInstanceIds.delete(id));
        }
        callbacks.onVisibilityChange();
        syncTreeCheckboxes();
      });

      attachTreeSelectionHandlers(componentItem, () => {
        selectTreeItem('component', componentGuid);
        callbacks.onSelectComponent(componentGuid);
      });

      entityChildren.appendChild(componentItem);
    });

    const entityCheckbox = entityItem.querySelector('.tree-checkbox') as HTMLInputElement;
    const allEntityInstanceIds = componentGuidEntries.flatMap(([, ids]) => ids);
    entityCheckbox.checked = allEntityInstanceIds.every((id) => state.visibleInstanceIds.has(id));
    entityCheckbox.addEventListener('change', (e) => {
      if ((e.target as HTMLInputElement).checked) {
        allEntityInstanceIds.forEach((id) => state.visibleInstanceIds.add(id));
      } else {
        allEntityInstanceIds.forEach((id) => state.visibleInstanceIds.delete(id));
      }
      callbacks.onVisibilityChange();
      syncTreeCheckboxes();
    });

    attachTreeSelectionHandlers(entityItem, () => {
      selectTreeItem('entity', entityNode.entityGuid);
      callbacks.onSelectEntity(entityNode.entityGuid);
    });

    entityItem.appendChild(entityChildren);
    rootChildren.appendChild(entityItem);
  });

  const rootCheckbox = rootItem.querySelector('.tree-checkbox') as HTMLInputElement;
  rootCheckbox.checked = state.visibleInstanceIds.size === state.flat.instancesById.size;
  rootCheckbox.addEventListener('change', (e) => {
    if ((e.target as HTMLInputElement).checked) {
      state.flat.instancesById.forEach((instance) => state.visibleInstanceIds.add(instance.instanceId));
    } else {
      state.visibleInstanceIds.clear();
    }
    callbacks.onVisibilityChange();
    syncTreeCheckboxes();
  });

  attachTreeSelectionHandlers(rootItem, () => {
    clearTreeAndSelection();
    callbacks.onClearSelection();
  });

  rootItem.appendChild(rootChildren);
  container.appendChild(rootItem);
}

export function syncTreeCheckboxes(): void {
  const container = document.getElementById('treeContainer');
  if (!container) return;

  container.querySelectorAll('.tree-item[data-type="component"]').forEach((item) => {
    const el = item as HTMLElement;
    const ids: string[] = JSON.parse(el.dataset.instanceIds || '[]');
    const checkbox = el.querySelector('.tree-checkbox') as HTMLInputElement;
    checkbox.checked = ids.length > 0 && ids.every((id) => state.visibleInstanceIds.has(id));
  });

  container.querySelectorAll('.tree-item[data-type="entity"]').forEach((item) => {
    const el = item as HTMLElement;
    const guid = el.dataset.guid!;
    const entityNode = state.flat.entities.get(guid);
    if (!entityNode) return;
    const ids = Array.from(entityNode.componentGuids.values()).flat();
    const checkbox = el.querySelector('.tree-checkbox') as HTMLInputElement;
    checkbox.checked = ids.length > 0 && ids.every((id) => state.visibleInstanceIds.has(id));
  });

  const root = container.querySelector('.tree-item[data-type="root"]');
  if (root) {
    const rootCheckbox = root.querySelector('.tree-checkbox') as HTMLInputElement;
    rootCheckbox.checked =
      state.flat.instancesById.size > 0 && state.visibleInstanceIds.size === state.flat.instancesById.size;
  }
}

export function clearTreeAndSelection(): void {
  document.querySelectorAll('.tree-item.selected').forEach((node) => node.classList.remove('selected'));
  state.selectedEntityGuid = null;
  state.selectedComponentGuid = null;
  state.selectedInstanceId = null;
}

function findComponentTreeItemByInstanceId(instanceId: string | null): HTMLElement | null {
  if (!instanceId) return null;
  const componentItems = document.querySelectorAll('.tree-item[data-type="component"]');
  for (const item of Array.from(componentItems)) {
    const el = item as HTMLElement;
    const ids: string[] = JSON.parse(el.dataset.instanceIds || '[]');
    if (ids.includes(instanceId)) return el;
  }
  return null;
}

export function selectTreeItem(type: 'entity' | 'component', guid: string, preferredInstanceId: string | null = null): void {
  clearTreeAndSelection();

  if (type === 'entity') {
    state.selectedEntityGuid = guid;
    const entityNode = state.flat.entities.get(guid);
    if (!entityNode) return;
    const allIds = Array.from(entityNode.componentGuids.values()).flat();
    const selectedId = allIds.find((id) => state.visibleInstanceIds.has(id)) || null;

    const selector = `.tree-item[data-type="${type}"][data-guid="${cssEscape(guid)}"]`;
    const item = document.querySelector(selector) as HTMLElement | null;
    if (item) {
      item.classList.add('selected');
      expandToItem(item);
      item.scrollIntoView({ block: 'center' });
    }

    state.selectedInstanceId = selectedId;
    return;
  }

  state.selectedComponentGuid = guid;
  const allInstanceIds = state.flat.componentsByGuid.get(guid) || [];
  if (!allInstanceIds.length) {
    state.selectedInstanceId = null;
    return;
  }

  let selectedId: string | null = null;
  if (preferredInstanceId && allInstanceIds.includes(preferredInstanceId)) {
    selectedId = state.visibleInstanceIds.has(preferredInstanceId) ? preferredInstanceId : null;
  } else {
    selectedId = allInstanceIds.find((id) => state.visibleInstanceIds.has(id)) || null;
  }

  if (!selectedId) {
    state.selectedInstanceId = null;
    return;
  }

  let item: HTMLElement | null = null;
  if (preferredInstanceId) {
    item = findComponentTreeItemByInstanceId(selectedId);
  }
  if (!item) {
    const selector = `.tree-item[data-type="${type}"][data-guid="${cssEscape(guid)}"]`;
    item = document.querySelector(selector);
  }
  if (item) {
    item.classList.add('selected');
    expandToItem(item);
    item.scrollIntoView({ block: 'center' });
  }

  state.selectedInstanceId = selectedId;
}
