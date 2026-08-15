import type { Component } from './types';

/** Normalizes a query-line address into a fetchable URL. Relative to this
 * page's own origin (works under Vite's dev proxy and in production alike)
 * instead of the old viewer.html's hardcoded http://localhost:5000. */
export function normalizeQueryUrl(input: string): string {
  const trimmed = (input || '').trim();
  if (!trimmed) return '';
  if (trimmed.startsWith('http://') || trimmed.startsWith('https://')) return trimmed;
  if (trimmed.startsWith('/')) return trimmed;
  if (trimmed.startsWith('api/')) return `/${trimmed}`;
  return `/api/${trimmed}`;
}

export async function fetchJson(url: string): Promise<any> {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  const data = await response.json();
  if (data?.error) throw new Error(data.error);
  return data;
}

/** Flattens whatever shape a REST endpoint returns (already-flat component
 * array, {model: [components]} map, GUID-only lookups) into a plain list of
 * components tagged with their source model. */
export async function normalizeApiToComponents(url: string, apiData: any): Promise<Component[]> {
  const urlObj = new URL(url, window.location.origin);
  const endpoint = urlObj.pathname;
  const baseOrigin = urlObj.origin;

  if (endpoint.includes('/components')) {
    if (Array.isArray(apiData)) {
      return apiData.map((component) => ({
        ...component,
        _model: component._model || component.model || 'DefaultModel',
      }));
    }
    if (apiData && typeof apiData === 'object') {
      const components: Component[] = [];
      Object.entries(apiData).forEach(([modelName, modelComponents]) => {
        if (!Array.isArray(modelComponents)) return;
        modelComponents.forEach((component: Component) => {
          components.push({ ...component, _model: component._model || modelName });
        });
      });
      return components;
    }
    return [];
  }

  if (endpoint.includes('/componentGuids') && apiData && typeof apiData === 'object') {
    const allGuids: string[] = [];
    Object.values(apiData).forEach((guids) => {
      if (Array.isArray(guids)) allGuids.push(...(guids as string[]));
    });
    if (!allGuids.length) return [];
    const compUrl = `${baseOrigin}/api/components?componentGuids=${encodeURIComponent(allGuids.join(','))}`;
    const compData = await fetchJson(compUrl);
    return normalizeApiToComponents(compUrl, compData);
  }

  if (endpoint.includes('/entityGuids') && apiData && typeof apiData === 'object') {
    const tasks: Promise<any>[] = [];
    Object.entries(apiData).forEach(([modelName, entityGuids]) => {
      if (!Array.isArray(entityGuids) || !entityGuids.length) return;
      const entityPart = encodeURIComponent((entityGuids as string[]).join(','));
      const modelPart = encodeURIComponent(modelName);
      tasks.push(fetchJson(`${baseOrigin}/api/components?models=${modelPart}&entityGuids=${entityPart}`));
    });
    const responses = await Promise.all(tasks);
    const all: Component[] = [];
    for (const response of responses) {
      const normalized = await normalizeApiToComponents(`${baseOrigin}/api/components`, response);
      all.push(...normalized);
    }
    return all;
  }

  return [];
}
