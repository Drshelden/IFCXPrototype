import type { AppState, Component, Instance } from './types';

/** Rebuilds state.flat (entities / componentsByGuid / instancesById) from
 * every query line's last result set. Ported from viewer.html's
 * rebuildFlatState — same grouping behavior, independent of the 3D pipeline. */
export function rebuildFlatState(state: AppState): void {
  const entities: AppState['flat']['entities'] = new Map();
  const componentsByGuid: AppState['flat']['componentsByGuid'] = new Map();
  const instancesById: AppState['flat']['instancesById'] = new Map();

  state.queryResults.forEach((components, queryId) => {
    const queryIndex = state.queryLines.findIndex((q) => q.id === queryId);
    components.forEach((component: Component, idx: number) => {
      const componentGuid = component.componentGuid;
      if (!componentGuid) return;
      const entityGuid = component.entityGuid || 'Unknown';
      const modelName = component._model || (component as any).model || 'UnknownModel';
      const instanceId = `${queryId}::${modelName}::${componentGuid}::${idx}`;

      const instance: Instance = {
        instanceId,
        componentGuid,
        entityGuid,
        modelName,
        queryId,
        queryIndex,
        component: { ...component, _model: modelName, _query: queryIndex },
      };

      instancesById.set(instanceId, instance);

      if (!entities.has(entityGuid)) {
        entities.set(entityGuid, { entityGuid, componentGuids: new Map() });
      }
      const entityNode = entities.get(entityGuid)!;
      if (!entityNode.componentGuids.has(componentGuid)) {
        entityNode.componentGuids.set(componentGuid, []);
      }
      entityNode.componentGuids.get(componentGuid)!.push(instanceId);

      if (!componentsByGuid.has(componentGuid)) componentsByGuid.set(componentGuid, []);
      componentsByGuid.get(componentGuid)!.push(instanceId);
    });
  });

  state.flat = { entities, componentsByGuid, instancesById };

  if (!state.visibleInstanceIds.size) {
    instancesById.forEach((instance) => state.visibleInstanceIds.add(instance.instanceId));
  } else {
    const kept = new Set<string>();
    state.visibleInstanceIds.forEach((id) => {
      if (instancesById.has(id)) kept.add(id);
    });
    if (!kept.size) instancesById.forEach((instance) => kept.add(instance.instanceId));
    state.visibleInstanceIds = kept;
  }

  if (state.selectedInstanceId && !instancesById.has(state.selectedInstanceId)) {
    state.selectedInstanceId = null;
  }
}
