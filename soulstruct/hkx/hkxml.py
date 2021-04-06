import struct
import typing as tp
from xml.etree import ElementTree
from pathlib import Path

from .nodes import HKXNode
from .types import HKXType, HKXTypeList
from .enums import *


class HKXXMLParser:

    node_elements: list[ElementTree.Element]
    nodes: dict[int, HKXNode]
    root: HKXNode

    def __init__(self, input_file_path: Path):

        with Path(input_file_path).open("r") as f:
            input_xml = f.read()

        self.hkx_types = HKXTypeList.load_2015()  # TODO: choose or detect version

        root_element = ElementTree.fromstring(input_xml)
        self.node_elements = list(root_element.findall("object"))
        self.node_elements.sort(
            key=lambda e: self.parse_node_id(e.get("id"))
        )
        self.nodes = {}

        for i, node_element in enumerate(self.node_elements):
            if node_element.get("type") == "hkRootLevelContainer":
                self.root = self.parse_node_pointer(i + 1)
                break
        else:
            raise ValueError(f"Could not find 'hkRootLevelContainer' object in HKX XML.")

    def find_type(self, name: str) -> HKXType:
        name = name.replace("::", "")
        for hkx_type in self.hkx_types:
            if hkx_type and hkx_type.name.replace("::", "") == name:
                return hkx_type

    def parse_node_id(self, id_string: str) -> int:
        """Reference to a top-level HKX node (represents a pointer)."""
        if id_string.startswith("#"):
            return int(id_string[1:])
        return 0

    def parse_float(self, int_string: str) -> float:
        """`int_string` should have hex format "x123456ab"."""
        return struct.unpack("f", struct.pack("I", int(int_string[1:], 16)))[0]

    def split_numeric_array(self, text: str) -> list[str]:
        stripped_text = text.strip().replace("\n", "").replace("\r", "")
        return [x for x in stripped_text.split(" ") if x]

    def parse_numeric_array(self, hkx_type: HKXType, text: str):
        return [self.parse_value_text(hkx_type, n) for n in self.split_numeric_array(text)]

    def parse_array(self, hkx_type: HKXType, element: ElementTree.Element) -> HKXNode:
        pointer_type = hkx_type.get_base_type(self.hkx_types).get_pointer_base_type(self.hkx_types)
        if pointer_type.tag_data_type in {TagDataType.Bool, TagDataType.Int, TagDataType.Float}:
            value = self.parse_numeric_array(
                hkx_type.get_base_type(self.hkx_types).get_pointer_type(self.hkx_types), element.text
            )
        else:
            value = [self.parse_value(hkx_type.get_base_type(self.hkx_types).pointer, x) for x in element]
        return HKXNode([x for x in value if x], hkx_type)

    def parse_value_text(self, hkx_type: HKXType, text: str) -> HKXNode:
        if hkx_type.get_base_type(self.hkx_types).tag_data_type == TagDataType.Bool:
            value = bool(text)
        elif hkx_type.get_base_type(self.hkx_types).tag_data_type == TagDataType.Int:
            value = int(text)
        elif hkx_type.get_base_type(self.hkx_types).tag_data_type == TagDataType.Float:
            value = self.parse_float(text)
        else:
            value = None
        return HKXNode(value, hkx_type)

    def parse_value(self, hkx_type: HKXType, element: ElementTree.Element) -> HKXNode:
        if hkx_type.get_base_type(self.hkx_types).tag_data_type == TagDataType.String:
            return HKXNode(element.text, hkx_type)

        elif TagDataType.Bool <= hkx_type.get_base_type(self.hkx_types).tag_data_type <= TagDataType.Float:
            return self.parse_value_text(hkx_type, element.text)

        elif hkx_type.get_base_type(self.hkx_types).tag_data_type == TagDataType.Pointer:
            return HKXNode(
                value=self.parse_node_pointer(self.parse_node_id(element.text)),
                hkx_type=hkx_type,
            )

        elif hkx_type.get_base_type(self.hkx_types).tag_data_type == TagDataType.Class:
            members = {member.name: member for member in hkx_type.get_base_type(self.hkx_types).all_members}

            for member_element in element:
                name = member_element.get("name")
                value = self.parse_value(members[name].hkx_type, member_element)

                if value is None or value.value is None or value.hkx_type is None:
                    raise ValueError(f"Invalid XML value parsed: name {name}, type {hkx_type}, value {value}")

                members[name] = value

            if hkx_type.get_base_type(self.hkx_types).name == "hkQsTransformf":
                floats = [
                    HKXNode(self.parse_float(int_str), self.find_type("float"))
                    for int_str in self.split_numeric_array(element.text)
                ]

                members["translation"] = HKXNode(floats[:4], members["translation"].hkx_type)
                members["rotation"] = HKXNode(floats[4:8], members["rotation"].hkx_type)
                members["scale"] = HKXNode(floats[8:12], members["scale"].hkx_type)

            return HKXNode({x: y for x, y in members.items() if isinstance(y, HKXNode)}, hkx_type)

        elif hkx_type.get_base_type(self.hkx_types).tag_data_type & 0xF == TagDataType.Array:
            return self.parse_array(hkx_type, element)

    def parse_node_pointer(self, node_id: int) -> HKXNode:
        """Retrieve node indexed (in XML) by `node_id`, or create it."""
        if node_id in self.nodes:
            return self.nodes[node_id]

        node_element = self.node_elements[node_id - 1]
        hkx_type = self.find_type(node_element.get("type"))
        if hkx_type is None:
            raise TypeError(f"Type '{node_element.get('type')}' could not be found in the type database.")
        self.nodes[node_id] = self.parse_value(hkx_type, node_element)
        if self.nodes[node_id].value is None:
            raise ValueError(
                f"Node with null value parsed from XML: type {hkx_type.name}, {hkx_type.get_base_type(self.hkx_types).tag_data_type}"
            )


class HKXXMLSerializer:

    SPECIAL_TYPE_NAMES = {
        "hkcdStaticTreeDynamicStoragehkcdStaticTreeCodec3Axis4": "hkcdStaticTreeDynamicStorage4",
        "hkcdStaticTreeDynamicStoragehkcdStaticTreeCodec3Axis5": "hkcdStaticTreeDynamicStorage5",
        "hkcdStaticTreeDynamicStoragehkcdStaticTreeCodec3Axis6": "hkcdStaticTreeDynamicStorage6",
        "hkcdStaticTreeTreehkcdStaticTreeDynamicStorage6": "hkcdStaticTreeDefaultTreeStorage6"
    }

    hkx_types: HKXTypeList
    nodes: list[HKXNode, ...]
    backporter: tp.Optional[tp.Callable[[list[HKXType]], list[HKXType]]]

    def __init__(self, root_node: HKXNode, with_backport=False):
        self.hkx_types = HKXTypeList([])
        self.hkx_type_tags = {}  # maps type names to XML tag strings
        self.nodes = []
        self.with_backport = with_backport  # TODO: Not doing anything with this (not sure if XML write needs it).
        self.serialized = self.serialize(root_node)  # type: ElementTree.Element

    def write(self, xml_file_path: Path, encoding: str = None):
        xml_file_path = Path(xml_file_path)
        mode = "w" if encoding == "unicode" else "wb"
        with xml_file_path.open(mode) as f:
            # if encoding is None:
            #     f.write(b"<?xml version='1.0' encoding=\"ascii\"?>\n")
            xml_str = ElementTree.tostring(self.serialized, encoding=encoding)
            f.write(xml_str)

    def serialize(self, root_node: HKXNode):
        self.nodes.append(root_node)
        root_node.attached_item = len(self.nodes)
        self._scan_node_for_types(root_node)

        # TODO: Always this SDK version string?
        root_element = ElementTree.Element("hktagfile", {"version": "1", "sdkversion": "hk_2012.2.0-r1"})

        for hkx_type in self.hkx_types:
            # TODO: "hkQsTransformf" is not serialized, but is instead converted into a `vec12` tag for the XML.
            #  This is probably a shortcut handled by AssetCc2.exe, but I'll skip it, so I probably do want to
            #  serialize the type here.
            if hkx_type.tag_data_type == TagDataType.Class and hkx_type.name != "hkQsTransformf":
                self.serialize_type(root_element, hkx_type)

        for child_node in self.nodes:
            element = self.serialize_node(root_element, child_node)
            element.set("id", self.get_id_string(child_node.attached_item))
            element.set("type", self.hkx_type_tags[child_node.hkx_type.get_base_type(self.hkx_types)])
            element.tag = "object"

        HKXXMLSerializer.indent(root_element)
        return root_element

    def serialize_node(self, parent_element: ElementTree.Element, node: HKXNode) -> ElementTree.Element:
        if node.value or hasattr(node.value, "__len__") and len(node.value) > 0:
            element = ElementTree.SubElement(parent_element, self.get_sub_type_name(node.hkx_type))

            hkx_type = node.hkx_type.get_base_type(self.hkx_types)

            if hkx_type.tag_data_type == TagDataType.Bool:
                element.text = str(1 if node.value else 0)

            elif hkx_type.tag_data_type == TagDataType.String:
                element.text = node.value

            elif hkx_type.tag_data_type == TagDataType.Int:
                element.text = str(node.value)

            elif hkx_type.tag_data_type == TagDataType.Float:
                element.text = self.get_float_string(node.value)

            elif hkx_type.tag_data_type == TagDataType.Pointer:
                element.text = self.get_id_string(node.value.attached_item)

            elif hkx_type.tag_data_type == TagDataType.Class:
                # hkQsTransformf
                # TODO: Why convert this special case to 'vec12' tag and float strings?
                #  Must be for `AssetCc2.exe` specifically. Remove it, I think.
                if hkx_type.name == "hkQsTransformf":
                    flattened_nodes = (
                        node.value["translation"].value +
                        node.value["rotation"].value +
                        node.value["scale"].value
                    )
                    floats = [float_node.value for float_node in flattened_nodes]
                    element.tag = "vec12"
                    element.text = " ".join([self.get_float_string(x) for x in floats])

                else:
                    for member in hkx_type.all_members:
                        if not member.flags & 1 and member.name in node.value:
                            member_elem = self.serialize_node(element, node.value[member.name])

                            if member_elem is not None:
                                member_elem.set("name", member.name)

                            if member.tag:
                                member_elem.tag = self.get_sub_type_name(member.tag)

            elif hkx_type.tag_data_type & 0xF == TagDataType.Array:
                pointer = hkx_type.get_base_type(self.hkx_types)

                if pointer.tag_data_type == TagDataType.Bool or pointer.tag_data_type == TagDataType.Int:
                    element.text = self.make_num_array(node)

                elif pointer.tag_data_type == TagDataType.Float:
                    element.text = " ".join([self.get_float_string(x.value) for x in node.value])

                else:
                    for child_obj in node.value:
                        self.serialize_node(element, child_obj)

                if hkx_type.tag_data_type == TagDataType.Array:
                    element.set("size", str(len(node.value)))

                elif hkx_type.tag_data_type == TagDataType.Tuple:
                    element.set("size", str(hkx_type.tuple_size))

                # hkVector4
                if hkx_type.tuple_size == 4 and pointer.tag_data_type == TagDataType.Float:
                    element.tag = "vec4"
                    element.attrib.pop("size")

                # hkMatrix4f
                elif hkx_type.tuple_size == 16 and pointer.tag_data_type == TagDataType.Float:
                    element.tag = "vec16"
                    element.attrib.pop("size")

            return element

    def serialize_type(self, parent: ElementTree.Element, hkx_type: HKXType):
        element = ElementTree.SubElement(parent, "class")
        element.set("name", self.hkx_type_tags[hkx_type])
        element.set("version", str(hkx_type.version))

        if hkx_type.parent is not None:
            element.set("parent", self.hkx_type_tags[hkx_type.parent])

        for member in hkx_type.members:
            member_elem = ElementTree.SubElement(element, "member")
            member_elem.set("name", member.name)
            self.serialize_member_prop(member_elem, member.tag if member.tag else member.hkx_type)

            if member.flags & 1:
                member_elem.set("type", "void")

        return element

    def serialize_member_prop(self, parent, hkx_type: HKXType):
        if hkx_type is None:
            return

        hkx_type = hkx_type.get_base_type(self.hkx_types)

        parent.set("type", self.get_sub_type_name(hkx_type))

        if hkx_type.tag_data_type == TagDataType.Pointer:
            parent.set("class", self.hkx_type_tags[hkx_type.pointer])

        elif hkx_type.tag_data_type == TagDataType.Class:
            if hkx_type.name == "hkQsTransformf":
                parent.set("type", "vec12")
            else:
                parent.set("class", self.hkx_type_tags[hkx_type])

        elif hkx_type.tag_data_type == TagDataType.Array:
            parent.set("array", "true")
            self.serialize_member_prop(parent, hkx_type.pointer)

        elif hkx_type.tag_data_type == TagDataType.Tuple:
            if hkx_type.pointer.get_base_type(self.hkx_types).tag_data_type == TagDataType.Float and hkx_type.tuple_size == 4:
                parent.set("type", "vec4")

            elif hkx_type.pointer.get_base_type(self.hkx_types).tag_data_type == TagDataType.Float and hkx_type.tuple_size == 16:
                parent.set("type", "vec16")

            else:
                parent.set("count", str(hkx_type.tuple_size))
                self.serialize_member_prop(parent, hkx_type.pointer)

    def get_sub_type_name(self, hkx_type: HKXType) -> str:
        hkx_type = hkx_type.get_base_type(self.hkx_types)
        if hkx_type.tag_data_type == TagDataType.Bool or hkx_type.tag_data_type == TagDataType.Int:
            if hkx_type.tag_type_flags & TagDataType.Int8:
                return "byte"
            else:
                return "int"
        elif hkx_type.tag_data_type == TagDataType.String:
            return "string"
        elif hkx_type.tag_data_type == TagDataType.Float:
            return "real"
        elif hkx_type.tag_data_type == TagDataType.Pointer:
            return "ref"
        elif hkx_type.tag_data_type == TagDataType.Class:
            return "struct"
        elif hkx_type.tag_data_type == TagDataType.Array:
            return "array"
        elif hkx_type.tag_data_type == TagDataType.Tuple:
            return "tuple"
        return ""

    @staticmethod
    def get_float_string(value: float) -> str:
        return f"x{struct.unpack('I', struct.pack('f', value))[0]:08x}"

    def get_value_string(self, obj: HKXNode) -> str:
        hkx_type = obj.get_base_type(self.hkx_types)
        if hkx_type.tag_data_type == TagDataType.Bool:
            return str(1 if obj.value else 0)
        elif hkx_type.tag_data_type == TagDataType.Int:
            return str(obj.value)
        elif hkx_type.tag_data_type == TagDataType.Float:
            return self.get_float_string(obj.value)

    def make_num_array(self, node: HKXNode) -> str:
        index = 16 if node.get_base_type(self.hkx_types).pointer.get_base_type(self.hkx_types).byte_size == 1 else 8
        result = ""
        for i in range(len(node.value)):
            if not i % index:
                result += "\n"
            result += self.get_value_string(node.value[i]) + " "
        return result[:-1]

    @staticmethod
    def get_id_string(index):
        return f"#{index:04}"

    def set_xml_tag(self, hkx_type: HKXType) -> str:
        """Set XML tag of given `hkx_type`, based on its super type (called recursively before serialization begins)."""
        original_hkx_type, hkx_type = hkx_type, hkx_type.get_base_type(self.hkx_types)
        name = hkx_type.name
        for template in hkx_type.templates:
            name += self.set_xml_tag(template.hkx_type) if template.hkx_type else str(template.value)
        xml_tag = self.hkx_type_tags[hkx_type] = name.replace(":", "").replace(" ", "")
        return xml_tag

    def _scan_hkx_types(self, hkx_type: HKXType):
        if hkx_type in self.hkx_types:
            return  # already scanned

        if hkx_type.parent_type_index:
            self._scan_hkx_types(hkx_type.parent)
        if hkx_type.pointer:
            self._scan_hkx_types(hkx_type.pointer)

        self.hkx_types.append(hkx_type)  # after parent and pointer types

        for member in hkx_type.members:
            self._scan_hkx_types(member.hkx_type)

        self.set_xml_tag(hkx_type)

        if hkx_type.tag in self.SPECIAL_TYPE_NAMES:
            # Create a fake type.
            special_name = self.SPECIAL_TYPE_NAMES[hkx_type.tag]
            fake_type = HKXType(special_name)
            fake_type.tag_type_flags = 7
            fake_type.tag = special_name
            fake_type.parent = HKXType(name=hkx_type.tag)
            self.hkx_types.append(fake_type)

            hkx_type.tag = special_name

    def _scan_node_for_types(self, node: HKXNode):
        if node is None:
            return

        self._scan_hkx_types(node.hkx_type)

        if (
            node.get_base_type(self.hkx_types).tag_data_type == TagDataType.Pointer
            and node.value and not node.value.attached_item
        ):
            self.nodes.append(node.value)
            node.value.attached_item = len(self.nodes)

            self._scan_node_for_types(node.value)

        elif node.get_base_type(self.hkx_types).tag_data_type == TagDataType.Class:
            for member in node.hkx_type.all_members:
                if member.name in node.value:
                    self._scan_node_for_types(node.value[member.name])

        elif node.get_base_type(self.hkx_types).tag_data_type & 0xF == TagDataType.Array:
            for array_obj in node.value:
                self._scan_node_for_types(array_obj)

    @staticmethod
    def indent(element: ElementTree.Element, level=0, hor="  ", ver="\n"):
        i = ver + level * hor
        if len(element):
            if not element.text or not element.text.strip():
                element.text = i + hor
            if not element.tail or not element.tail.strip():
                element.tail = i
            for element in element:
                HKXXMLSerializer.indent(element, level + 1, hor, ver)
            if not element.tail or not element.tail.strip():
                element.tail = i
        else:
            if level and (not element.tail or not element.tail.strip()):
                element.tail = i
                if element.text and element.text.startswith("\n"):
                    element.text = element.text.replace("\n", i + hor) + i
                elif (element.tag == "class" or element.tag == "struct") and not len(element):
                    element.text = i
