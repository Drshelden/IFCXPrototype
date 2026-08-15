export type Component = Record<string, unknown> & {
  componentGuid?: string;
  componentType?: string;
  entityGuid?: string;
  entityType?: string;
  componentName?: string;
  _model?: string;
  _query?: number;
};

export interface Instance {
  instanceId: string;
  componentGuid: string;
  entityGuid: string;
  modelName: string;
  queryId: number;
  queryIndex: number;
  component: Component;
}

export interface EntityNode {
  entityGuid: string;
  componentGuids: Map<string, string[]>; // componentGuid -> instanceIds
}

export interface FlatState {
  entities: Map<string, EntityNode>;
  componentsByGuid: Map<string, string[]>; // componentGuid -> instanceIds
  instancesById: Map<string, Instance>;
}

export interface QueryLine {
  id: number;
  address: string;
  repeatEnabled: boolean;
  repeatTimer: ReturnType<typeof setInterval> | null;
  lastResultCount: number;
  lastRunAt: Date | null;
  index: number;
}

export interface DataTab {
  tabId: string;
  label: string;
  instanceId: string;
}

export interface AppState {
  nextQueryId: number;
  queryLines: QueryLine[];
  queryResults: Map<number, Component[]>;
  flat: FlatState;
  visibleInstanceIds: Set<string>;
  selectedInstanceId: string | null;
  selectedEntityGuid: string | null;
  selectedComponentGuid: string | null;
  dataTabs: DataTab[];
  activeTabId: string | null;
}

export function createInitialState(): AppState {
  return {
    nextQueryId: 1,
    queryLines: [],
    queryResults: new Map(),
    flat: {
      entities: new Map(),
      componentsByGuid: new Map(),
      instancesById: new Map(),
    },
    visibleInstanceIds: new Set(),
    selectedInstanceId: null,
    selectedEntityGuid: null,
    selectedComponentGuid: null,
    dataTabs: [],
    activeTabId: null,
  };
}
