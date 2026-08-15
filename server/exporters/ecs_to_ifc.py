"""ECS component JSON -> IFC4 STEP file exporter.

Mirrors server/ingestors/ifc4ingestor.py in reverse: that module turns an
uploaded .ifc file into this repo's flat "ECS component" JSON; this module
turns ECS component JSON back into a real, valid IFC4 SPF file so external
IFC tooling (ifclite) can parse it natively. ECS components never carry a
placement/matrix or unit assignment (ifc4ingestor.py bakes geometry into
world coordinates and strips objectplacement/unitsincontext), so this
exporter always places entities at the model's identity WCS and fixes the
unit system to SI metres.

Uses ifcopenshell (already a project dependency) to build and serialize the
model, rather than hand-writing STEP text, so GlobalId encoding, header
formatting and schema validity are handled by a library that already gets
it right.
"""

import time

import ifcopenshell
import ifcopenshell.guid as guid
import ifcopenshell.ifcopenshell_wrapper as ifcopenshell_wrapper


def _compress_guid(entity_guid):
    """Compress a standard dashed UUID (as stored in ECS components) into
    an IFC-format 22-char GlobalId."""
    return guid.compress(entity_guid)


class ECS2IFC:
    """Converts a flat list of ECS component dicts (as produced by
    IFC2JSONSimple.spf2Json(), or returned by MemoryTree.get_components())
    for a single model into a real ifcopenshell.file.
    """

    def __init__(self, model_name, components):
        self.model_name = model_name
        self.components = components
        self.file = ifcopenshell.file(schema="IFC4")

        # entityGuid (or, for property sets, componentGuid) -> created
        # ifcopenshell entity. Unified so relationship components can
        # resolve either flavor of reference through one lookup.
        self._created = {}

        # entityGuid -> attribute component dict (IfcProject/IfcWall/etc.)
        self._attribute_components = {}
        # entityGuid -> IfcShapeRepresentationComponent dict
        self._shape_by_entity = {}
        # componentGuid -> IfcPropertySetComponent dict
        self._psets_by_guid = {}
        # list of relationship component dicts (componentType startswith IfcRel)
        self._relations = []

        self._schema_attr_cache = {}
        self._owner_history = None
        self._context = None

        self.express_id_map = {}

    # ------------------------------------------------------------------
    # Grouping
    # ------------------------------------------------------------------
    def _group_components(self):
        for component in self.components:
            component_type = component.get("componentType") or ""
            entity_guid = component.get("entityGuid")

            if component_type == "IfcShapeRepresentationComponent":
                if entity_guid:
                    self._shape_by_entity[entity_guid] = component
                continue

            if component_type == "IfcPropertySetComponent":
                component_guid = component.get("componentGuid")
                if component_guid:
                    self._psets_by_guid[component_guid] = component
                continue

            if component_type.startswith("IfcRel"):
                self._relations.append(component)
                continue

            # Everything else is an object-definition attribute component
            # (IfcProject, IfcSite, IfcWallStandardCase, IfcWallType, ...)
            if entity_guid and component.get("entityType"):
                self._attribute_components[entity_guid] = component

    # ------------------------------------------------------------------
    # Schema introspection helper
    # ------------------------------------------------------------------
    def _entity_attrs(self, entity_type):
        cached = self._schema_attr_cache.get(entity_type)
        if cached is None:
            schema = ifcopenshell_wrapper.schema_by_name("IFC4")
            decl = schema.declaration_by_name(entity_type)
            cached = {a.name() for a in decl.all_attributes()}
            self._schema_attr_cache[entity_type] = cached
        return cached

    def _build_kwargs(self, entity_type, component, base_kwargs):
        """Add the small curated set of simple ECS attributes (Name,
        Description, ObjectType, Tag, PredefinedType) that the target
        entity_type actually supports.

        ifc4ingestor.py's ATTRIBUTE_SUBSTITUTIONS never actually fires for
        Name/Description/HasPropertySets (its keys are capitalized but the
        attribute names it matches against are already lowerCamelCased by
        that point), so real stored components carry plain `name`/
        `description`, not `componentName`/`componentDescription`. Both are
        checked here so this keeps working if that's ever fixed upstream.
        """
        attrs = self._entity_attrs(entity_type)
        kwargs = dict(base_kwargs)
        simple_map = {
            "Name": component.get("componentName", component.get("name")),
            "Description": component.get("componentDescription", component.get("description")),
            "ObjectType": component.get("objectType"),
            "Tag": component.get("tag"),
            "LongName": component.get("longName"),
            "PredefinedType": component.get("predefinedType"),
            "Phase": component.get("phase"),
            "Elevation": component.get("elevation"),
        }
        for attr_name, value in simple_map.items():
            if value is not None and attr_name in attrs:
                kwargs[attr_name] = value
        return kwargs

    # ------------------------------------------------------------------
    # Boilerplate
    # ------------------------------------------------------------------
    def _create_boilerplate(self):
        f = self.file
        person = f.create_entity("IfcPerson", Identification="ecs-exporter")
        org = f.create_entity("IfcOrganization", Name="IFC-ECS")
        person_and_org = f.create_entity(
            "IfcPersonAndOrganization", ThePerson=person, TheOrganization=org
        )
        application = f.create_entity(
            "IfcApplication",
            ApplicationDeveloper=org,
            Version="1.0",
            ApplicationFullName="IFC-ECS ECS2IFC Exporter",
            ApplicationIdentifier="ifc-ecs-ecs2ifc",
        )
        self._owner_history = f.create_entity(
            "IfcOwnerHistory",
            OwningUser=person_and_org,
            OwningApplication=application,
            ChangeAction="ADDED",
            CreationDate=int(time.time()),
        )

        length_unit = f.create_entity("IfcSIUnit", UnitType="LENGTHUNIT", Name="METRE")
        self._units = f.create_entity("IfcUnitAssignment", Units=[length_unit])

        origin = f.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0))
        z_dir = f.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0))
        x_dir = f.create_entity("IfcDirection", DirectionRatios=(1.0, 0.0, 0.0))
        self._wcs = f.create_entity(
            "IfcAxis2Placement3D", Location=origin, Axis=z_dir, RefDirection=x_dir
        )
        self._context = f.create_entity(
            "IfcGeometricRepresentationContext",
            ContextType="Model",
            CoordinateSpaceDimension=3,
            Precision=1e-5,
            WorldCoordinateSystem=self._wcs,
        )

    def _identity_placement(self):
        # Geometry is already baked into world coordinates by the ingestor
        # (use-world-coords=True), so every entity gets an identity
        # placement relative to the model's WCS rather than a real offset.
        return self.file.create_entity(
            "IfcLocalPlacement", PlacementRelTo=None, RelativePlacement=self._wcs
        )

    # ------------------------------------------------------------------
    # Geometry
    # ------------------------------------------------------------------
    @staticmethod
    def _parse_obj(obj_text):
        vertices = []
        faces = []
        for line in obj_text.splitlines():
            parts = line.strip().split()
            if not parts:
                continue
            if parts[0] == "v" and len(parts) >= 4:
                vertices.append((float(parts[1]), float(parts[2]), float(parts[3])))
            elif parts[0] == "f" and len(parts) >= 4:
                face = tuple(int(p.split("/")[0]) for p in parts[1:4])
                faces.append(face)
        return vertices, faces

    def _build_shape(self, shape_component):
        items = shape_component.get("items") or []
        if not items or not isinstance(items[0], str):
            return None
        vertices, faces = self._parse_obj(items[0])
        if not vertices or not faces:
            return None

        f = self.file
        coords = f.create_entity("IfcCartesianPointList3D", CoordList=vertices)
        tfs = f.create_entity(
            "IfcTriangulatedFaceSet",
            Coordinates=coords,
            Normals=None,
            Closed=False,
            CoordIndex=faces,
        )
        shape_rep = f.create_entity(
            "IfcShapeRepresentation",
            ContextOfItems=self._context,
            RepresentationIdentifier="Body",
            RepresentationType="Tessellation",
            Items=[tfs],
        )
        return f.create_entity("IfcProductDefinitionShape", Representations=[shape_rep])

    # ------------------------------------------------------------------
    # Object definitions
    # ------------------------------------------------------------------
    def _create_object(self, entity_guid, component):
        entity_type = component["entityType"]
        f = self.file

        kwargs = {"GlobalId": _compress_guid(entity_guid), "OwnerHistory": self._owner_history}

        attrs = self._entity_attrs(entity_type)
        if "ObjectPlacement" in attrs:
            kwargs["ObjectPlacement"] = self._identity_placement()

        shape_component = self._shape_by_entity.get(entity_guid)
        if shape_component is not None and "Representation" in attrs:
            shape = self._build_shape(shape_component)
            if shape is not None:
                kwargs["Representation"] = shape

        kwargs = self._build_kwargs(entity_type, component, kwargs)

        entity = f.create_entity(entity_type, **kwargs)
        self._created[entity_guid] = entity
        self.express_id_map[entity_guid] = entity.id()
        return entity

    def _create_project_scaffolding(self):
        f = self.file
        for entity_guid, component in list(self._attribute_components.items()):
            entity_type = component["entityType"]
            if entity_type != "IfcProject":
                continue
            kwargs = self._build_kwargs(
                entity_type,
                component,
                {
                    "GlobalId": _compress_guid(entity_guid),
                    "OwnerHistory": self._owner_history,
                    "UnitsInContext": self._units,
                    "RepresentationContexts": [self._context],
                },
            )
            entity = f.create_entity(entity_type, **kwargs)
            self._created[entity_guid] = entity
            self.express_id_map[entity_guid] = entity.id()

    def _create_remaining_objects(self):
        for entity_guid, component in self._attribute_components.items():
            if entity_guid in self._created:
                continue
            self._create_object(entity_guid, component)

    def _create_property_sets(self):
        f = self.file
        for component_guid, component in self._psets_by_guid.items():
            properties = []
            for prop in component.get("hasProperties") or []:
                if not isinstance(prop, dict):
                    continue
                nominal_value = prop.get("nominalValue")
                wrapped_entity = None
                if isinstance(nominal_value, dict):
                    value_type = (nominal_value.get("componentType") or "").removesuffix(
                        "Component"
                    )
                    wrapped_value = nominal_value.get("wrappedValue")
                    if value_type and wrapped_value is not None:
                        try:
                            wrapped_entity = f.create_entity(value_type, wrapped_value)
                        except Exception:
                            wrapped_entity = None
                if prop.get("name") is None:
                    continue
                properties.append(
                    f.create_entity(
                        "IfcPropertySingleValue",
                        Name=prop["name"],
                        NominalValue=wrapped_entity,
                    )
                )

            pset = f.create_entity(
                "IfcPropertySet",
                GlobalId=_compress_guid(component_guid),
                OwnerHistory=self._owner_history,
                Name=component.get("name"),
                HasProperties=properties,
            )
            self._created[component_guid] = pset

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    def _resolve(self, entity_guid):
        return self._created.get(entity_guid)

    def _resolve_all(self, entity_guids):
        resolved = [self._resolve(g) for g in entity_guids or []]
        return [r for r in resolved if r is not None]

    def _create_relationships(self):
        f = self.file
        for component in self._relations:
            component_type = component.get("componentType") or ""
            component_guid = component.get("componentGuid")
            if not component_guid:
                continue

            if component_type == "IfcRelAggregatesComponent":
                relating = self._resolve(component.get("relatingObject"))
                related = self._resolve_all(component.get("relatedObjects"))
                if relating is None or not related:
                    continue
                f.create_entity(
                    "IfcRelAggregates",
                    GlobalId=_compress_guid(component_guid),
                    OwnerHistory=self._owner_history,
                    RelatingObject=relating,
                    RelatedObjects=related,
                )

            elif component_type == "IfcRelContainedInSpatialStructureComponent":
                relating = self._resolve(component.get("relatingStructure"))
                related = self._resolve_all(component.get("relatedElements"))
                if relating is None or not related:
                    continue
                f.create_entity(
                    "IfcRelContainedInSpatialStructure",
                    GlobalId=_compress_guid(component_guid),
                    OwnerHistory=self._owner_history,
                    RelatingStructure=relating,
                    RelatedElements=related,
                )

            elif component_type == "IfcRelDefinesByPropertiesComponent":
                relating = self._resolve(component.get("relatingPropertyDefinition"))
                related = self._resolve_all(component.get("relatedObjects"))
                if relating is None or not related:
                    continue
                f.create_entity(
                    "IfcRelDefinesByProperties",
                    GlobalId=_compress_guid(component_guid),
                    OwnerHistory=self._owner_history,
                    RelatedObjects=related,
                    RelatingPropertyDefinition=relating,
                )

            elif component_type == "IfcRelDefinesByTypeComponent":
                relating = self._resolve(component.get("relatingType"))
                related = self._resolve_all(component.get("relatedObjects"))
                if relating is None or not related:
                    continue
                f.create_entity(
                    "IfcRelDefinesByType",
                    GlobalId=_compress_guid(component_guid),
                    OwnerHistory=self._owner_history,
                    RelatedObjects=related,
                    RelatingType=relating,
                )

            # Other relationship kinds (materials, classifications, etc.)
            # are not required for viewing/property display and are
            # intentionally skipped.

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def build(self):
        self._group_components()
        self._create_boilerplate()
        self._create_project_scaffolding()
        self._create_remaining_objects()
        self._create_property_sets()
        self._create_relationships()
        return self.file

    def to_ifc(self, output_path):
        self.build()
        self.file.write(output_path)
        return self.express_id_map
