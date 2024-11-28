import json
import xml.etree.ElementTree as ET

# 解析 XML 文件
# tree = ET.parse(r'E:\xxx\apps\xxxMaterialsDatabase9.vmpd')
tree = ET.parse(r'xxxMaterialsDatabase9.vmpd')

# 获取根元素
root = tree.getroot()

# 根元素的标签
# print("Root element:", root.tag)

json_root = {"document_tree": {"materials": [], "dopants": []}}

# 查找所有___type="MaterialGroup" 的节点
for item in root.findall(".//*[@___Type='MaterialGroup']"):
    # 输出符合条件的节点的标签和属性
    # print(f"Found item: {item.tag}, Attributes: {item.attrib}")
    tmp = {}
    tmp["material_type"] = item.attrib["___Name"]
    tmp["material_items"] = []
    for child in item.findall(".//*[@___Type='Material']"):
        # print(f"Found item: {child.tag}, Attributes: {child.attrib}")
        material_item = {}
        material_item["name"] = child.attrib['___Name']

        visual_properties = child.find(".//visualProperties")
        if visual_properties is not None:
            color = visual_properties.find("color")
            if color is not None:
                red = int(color.attrib.get("___red"))
                green = int(color.attrib.get("___green"))
                blue = int(color.attrib.get("___blue"))
            transparency = visual_properties.find("transparency")
            if transparency is not None:
                transparency_value = transparency.attrib.get("___expression")
            visibility = visual_properties.find("visibility")
            if visibility is not None:
                visibility_value = visibility.attrib.get("___expression")

        visual_dict = {}
        visual_dict["color"] = [red, green, blue]
        visual_dict["transparency"] = int(transparency_value)
        visual_dict["visibility"] = True if visibility_value == "true" else False
        material_item["visual_properties"] = visual_dict

        physical_properties = child.find(".//physicalProperties2")
        if physical_properties is not None:
            density = physical_properties.find("density")
            if density is not None:
                # density_value = density.attrib.get("___activeMember")
                density_value = "Mass Density"
            chemicalFormula = physical_properties.find(".//chemicalFormula")
            chemicalFormula_value = chemicalFormula.attrib.get("___text")
            massDensity = physical_properties.find(".//massDensity")
            massDensity_value = massDensity.find("massDensity").attrib.get("___expression")
            physical_dict = {}
            physical_dict["density"] = density_value
            physical_dict["mass_density"] = {}
            physical_dict["mass_density"]["chemical_formula"] = chemicalFormula_value
            physical_dict["mass_density"]["density"] = 0 if len(massDensity_value) == 0 else float(massDensity_value)

            # print(visual_dict)
            # print(physical_dict)
            # break
            material_item["physical_properties"] = physical_dict

        # 查找type 标签
        type_tag = child.find(".//type")
        if type_tag is not None:
            material_item["material_type"] = type_tag.attrib.get("___activeMember")
            if type_tag.attrib.get("___activeMember").strip() == 'conductor':
                material_item["material_type"] = "Conductor"
                material_item["conductor"] = {}
                conductor_dict = {}
                bulkResistivity = type_tag.find(".//bulkResistivity")
                bulkResistivity_value = bulkResistivity.attrib.get("___expression")
                conductor_dict["bulk_resistivity"] = float(bulkResistivity_value)

                metal_workfunction = type_tag.find(".//metal_workfunction")
                metal_workfunction_value = metal_workfunction.attrib.get("___expression")
                conductor_dict["metal_work_function"] = float(metal_workfunction_value)

                sizeCorrection = type_tag.find(".//sizeCorrection")
                sizeCorrection_value = sizeCorrection.attrib.get("___activeMember").strip()
                conductor_dict["size_correction"] = "None" if sizeCorrection_value == 'none' else 'Exponential'

                conductor_dict["exponential"] = {}
                surfaceCorrection = type_tag.find(".//surfaceCorrection")
                surfaceCorrection_value = surfaceCorrection.attrib.get("___expression")
                meanFreePath = type_tag.find(".//meanFreePath")
                meanFreePath_value = meanFreePath.attrib.get("___expression")

                conductor_dict["exponential"]["correction_resistivity"] = 0 if len(
                    surfaceCorrection_value) == 0 else float(surfaceCorrection_value)
                conductor_dict["exponential"]["decay_length"] = 0 if len(meanFreePath_value) == 0 else float(
                    meanFreePath_value)
                conductor_dict["contact_resistivity"] = []
                material_item["conductor"] = conductor_dict
            else:
                material_item["material_type"] = "Dielectric"
                dielectricConstant = type_tag.find(".//dielectricConstant_")
                dielectricConstant_value = dielectricConstant.attrib.get("___expression")
                material_item["dielectric_constant"] = float(dielectricConstant_value)

            tmp["material_items"].append(material_item)
    json_root["document_tree"]["materials"].append(tmp)

for item in root.findall(".//*[@___Type='DopantGroup']"):
    tmp = {}
    tmp["dopant_items"] = []
    for child in item.findall(".//*[@___Type='Dopant']"):
        dopant_item = {}
        dopant_item["name"] = child.attrib.get("___Name")
        type_tag = child.find(".//type")
        if type_tag.attrib.get("___activeMember") == 'donor':
            type_value = "N-Type"
        elif type_tag.attrib.get("___activeMember") == 'acceptor':
            type_value = "P-Type"
        else:
            type_value = "Neutral"
        dopant_item["dopant_type"] = type_value
        # diffusionProperties
        dopant_item["diffusion_properties"] = []
        diffusionProperties = child.find(".//diffusionProperties")
        material_node_types = diffusionProperties.findall("*")
        for material_node in material_node_types:
            if material_node.tag.startswith("_MaterialNodeType"):
                t = {}
                t["material"] = material_node.attrib.get("UserDefinedName")
                activationEnergy = material_node.find("activationEnergy")
                t["activation_energy"] = float(activationEnergy.attrib.get("___expression"))
                maxDiffusionCoefficient = material_node.find("maxDiffusionCoefficient")
                t["max_diffusion_coefficient"] = float(maxDiffusionCoefficient.attrib.get("___expression"))
                dopant_item["diffusion_properties"].append(t)

        atomicNumber = child.find(".//atomicNumber")
        atomicNumber_value = 0 if len(atomicNumber.attrib.get("___expression")) == 0 else int(
            atomicNumber.attrib.get("___expression"))

        atomicWeight = child.find(".//atomicWeight")
        atomicWeight_value = 0 if len(atomicWeight.attrib.get("___expression")) == 0 else float(
            atomicWeight.attrib.get("___expression"))
        dopant_item["atomic_number"] = atomicNumber_value
        dopant_item["atomic_weight"] = atomicWeight_value

        tmp["dopant_items"].append(dopant_item)
    json_root["document_tree"]["dopants"].append(tmp)

with open('output.json', 'w') as rfile:
    json.dump(json_root, rfile, indent=4)
