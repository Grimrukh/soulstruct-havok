from __future__ import annotations

__all__ = [
    "Material",
    "Motion",
    "Shape",
    "ConvexShape",
    "SingleShapeContainer",
    "StorageExtendedMeshShapeMaterial",
    "StorageExtendedMeshShapeMeshSubpartStorage",
    "StorageExtendedMeshShapeShapeSubpartStorage",
    "ExtendedMeshShapeTrianglesSubpart",
    "ExtendedMeshShapeShapesSubpart",
    "FSCustomMeshParameter",
    "FSCustomParamStorageExtendedMeshShape",
    "LinkedCollidable",
    "Entity",
    "ConstraintData",
    "ConstraintAtom",
    "ModifierConstraintAtom",
    "ConstraintInstance",
    "Action",
    "MoppCodeCodeInfo",
    "MoppCode",
    "MoppBvTreeShape",
    "PhysicsSystem",
    "PhysicsData",
]

import typing as tp

import numpy as np

from soulstruct_havok.utilities.maths import Vector4


class BaseHK(tp.Protocol):
    
    @classmethod
    def get_type_name(cls) -> str:
        ...


class Material(BaseHK, tp.Protocol):
    responseType: int
    friction: float
    restitution: float


class Motion(BaseHK, tp.Protocol):
    type: int
    inertiaAndMassInv: Vector4
    linearVelocity: Vector4
    angularVelocity: Vector4
    savedQualityTypeIndex: int


class Shape(BaseHK, tp.Protocol):
    userData: int
    type: int


class ConvexShape(Shape, tp.Protocol):
    radius: float


class SingleShapeContainer(BaseHK, tp.Protocol):
    childShape: Shape


class StorageExtendedMeshShapeMaterial(BaseHK, tp.Protocol):
    # hkpMeshMaterial
    filterInfo: int
    # hkpStorageExtendedMeshShapeMaterial
    restitution: float
    friction: float
    userData: int


class StorageExtendedMeshShapeMeshSubpartStorage(BaseHK, tp.Protocol):
    vertices: np.ndarray  # `(n, 4)` float32 array
    # `indices8` not defined in early versions.
    indices16: list[int]
    indices32: list[int]
    materialIndices: list[int]
    # `materials` type differs in early versions (int).


class StorageExtendedMeshShapeShapeSubpartStorage(BaseHK, tp.Protocol):
    materialIndices: list[int]
    materials: list[StorageExtendedMeshShapeMaterial]
    materialIndices16: list[int]


class ExtendedMeshShapeTrianglesSubpart(BaseHK, tp.Protocol):
    numTriangleShapes: int
    vertexStriding: int
    numVertices: int
    extrusion: Vector4
    indexStriding: int
    stridingType: int
    flipAlternateTriangles: int
    triangleOffset: int


class ExtendedMeshShapeShapesSubpart(BaseHK, tp.Protocol):
    childShapes: list[ConvexShape]


class FSCustomMeshParameter(BaseHK, tp.Protocol):
    version: int
    vertexDataBuffer: list[int]
    materialNameData: int


class FSCustomParamStorageExtendedMeshShape(Shape, tp.Protocol):
    """Shares its name with FromSoft's custom subclass."""
    # hkpExtendedMeshShape
    aabbHalfExtents: Vector4
    aabbCenter: Vector4
    trianglesSubparts: list[ExtendedMeshShapeTrianglesSubpart]
    numTrianglesSubparts: int
    shapesSubparts: list[ExtendedMeshShapeShapesSubpart]
    numShapesSubparts: int
    embeddedTrianglesSubpart: ExtendedMeshShapeTrianglesSubpart
    # hkpStorageExtendedMeshShape
    meshstorage: list[StorageExtendedMeshShapeMeshSubpartStorage]
    shapestorage: list[StorageExtendedMeshShapeShapeSubpartStorage]
    # CustomParamStorageExtendedMeshShape
    materialArray: list[FSCustomMeshParameter]


class LinkedCollidable(BaseHK, tp.Protocol):
    # hkpCdBody
    shape: Shape
    shapeKey: int
    # hkpCollidable
    allowedPenetrationDepth: float
    # hkpLinkedCollidable
    linkedBody: tp.Any  # hkpRigidBody


class Entity(BaseHK, tp.Protocol):
    """NOTE: `hkpRigidBody` is a subclass of `hkpEntity` but defines no further fields."""

    # hkpWorldObject
    userData: int
    collidable: LinkedCollidable
    name: str

    # hkpEntity
    material: Material
    motion: Motion


class ConstraintData(BaseHK, tp.Protocol):
    userData: int


class ConstraintAtom(BaseHK, tp.Protocol):
    type: int


class ModifierConstraintAtom(BaseHK, tp.Protocol):
    modifierAtomSize: int
    childSize: int
    child: ConstraintAtom


class ConstraintInstance(BaseHK, tp.Protocol):
    data: ConstraintData
    constraintModifiers: ModifierConstraintAtom
    entities: tuple[Entity, ...]  # actually exactly two
    priority: int
    wantRuntime: bool
    name: str
    userData: int


class Action(BaseHK, tp.Protocol):
    userData: int
    name: str


class MoppCodeCodeInfo(BaseHK, tp.Protocol):
    offset: Vector4


class MoppCode(BaseHK, tp.Protocol):
    info: MoppCodeCodeInfo
    data: list[int]


class MoppBvTreeShape(Shape, tp.Protocol):
    # hkMoppBvTreeShapeBase
    code: MoppCode
    # hkpMoppBvTreeShape
    child: SingleShapeContainer


class PhysicsSystem(BaseHK, tp.Protocol):
    rigidBodies: list[Entity]
    constraints: list[ConstraintInstance]
    actions: list[Action]
    name: str
    userData: int


class PhysicsData(BaseHK, tp.Protocol):
    systems: list[PhysicsSystem]
