from chemlib import Compound, Element
from bs4 import BeautifulSoup

import requests

accent_letters = {
    "á":	"Ã¡",
    "é":	"Ã©",
    "í":	"Ã",
    "ó":	"Ã³",
    "ú":	"Ãº"}

oxidation_numbers = {
    "Ac": 3,
    "Al": 3,
    "Am": 3,
    "Sb": 3,
    "Ar": 0,
    "As": 3,
    "At": -1,
    "S": [-2, 2, 4, 6],
    "Ba": 2,
    "Be": 2,
    "Bk": 3,
    "Bi": 3,
    "Bh": None,
    "B": 3,
    "Br": [-1, 1, 3, 5, 7],
    "Cd": 2,
    "Ca": 2,
    "Cf": 3,
    "C": [-2, +2, +4],
    "Ce": 3,
    "Cs": 1,
    "Zr": 4,
    "Cl": [-1, 1, 3, 5, 7],
    "Co": [2, 3],
    "Cu": [1, 2],
    "Cn": None,
    "Cr": [2, 3, 4, 5, 6],
    "Cm": 3,
    "Ds": None,
    "Dy": 3,
    "Db": None,
    "Es": 3,
    "Er": 3,
    "Sc": 3,
    "Sn": [4, 2],
    "Sr": 2,
    "Eu": 3,
    "Fm": 3,
    "Fl": 2,
    "F": -1,
    "Fr": 1,
    "P": [-3, 3, 5],
    "Gd": 3,
    "Ga": 3,
    "Ge": 4,
    "Hf": 4,
    "Hs": None,
    "He": 0,
    "H": 1,
    "Fe": [2, 3],
    "Ho": 3,
    "In": 3,
    "Ir": [4, 1],
    "Yb": 3,
    "Y": 3,
    "Kr": 2,
    "La": 3,
    "Lr": 3,
    "Li": 1,
    "Lv": None,
    "Lu": 3,
    "Mg": 2,
    "Mn": [2, 4, 6, 7],
    "Mt": None,
    "Md": 3,
    "Hg": [1, 2],
    "Mo": 6,
    "Mc": None,
    "Nd": 3,
    "Np": 5,
    "Ne": 0,
    "Nh": 1,
    "Nb": 5,
    "N": [-3, 1, 2, 3, 4, 5],
    "No": 3,
    "Ni": 2,
    "Og": None,
    "Au": 3,
    "Os": 4,
    "O": -2,
    "Pd": 2,
    "Ag": 1,
    "Pt": [2, 4],
    "Pb": 2,
    "Pu": 4,
    "Po": 4,
    "K": 1,
    "Pr": 3,
    "Pm": 3,
    "Pa": 5,
    "Ra": 2,
    "Rn": 2,
    "Re": [4, 7],
    "Rh": 3,
    "Rg": None,
    "Rb": 1,
    "Ru": [3, 4],
    "Rf": 4,
    "Sm": 3,
    "Sg": None,
    "Se": 4,
    "Si": 4,
    "Na": 1,
    "Tl": 1,
    "Tc": 7,
    "Te": 4,
    "Ts": None,
    "Tb": 3,
    "Ti": 4,
    "Th": 4,
    "Tm": 3,
    "Ta": 5,
    "U": 6,
    "V": 5,
    "W": 6,
    "Xe": 8,
    "I": -1,
    "Zn": 2,
}

reactions = [["Metal", "Hydrogen"],
             (["Nm/Mll-16", "Hydrogen"], ["Nm/Mll-17", "Hydrogen"]),
             ["M", "Oxygen"],
             ["Nm/Mll", "Oxygen"],
             (["M-1", "Water"], ["M-2", "Water"]),
             ["MetalOxide", "Water"],
             ["Anhydride", "Water"],
             ["M", "Nm/Mll"],
             ["Metal", "Acid"],
             ["Hydroxide", "Acid"]]

# Lista de reacciones
# 1. Metal + Hidrogeno ---> Hidruro metalico
# 2. NoMetal + Hidrogeno ---> Hidruro no metalico / Hidracido
# 3. Metal + Oxigeno ---> Oxido metalico
# 4. NoMetal + Oxigeno ---> Oxido no metalico / Anhidrido
# 5. MetalActivo + Agua ---> Hidroxido + Hidrogeno
# 6. Oxido metalico + Agua ---> Hidroxido
# 7. Anhidrido + Agua ---> Oxoacido
# 8. Metal + NoMetal ---> Sal binaria
# 9. MetalActivo + Acido ---> Sal + Hidrogeno
# 10. Hidroxido + Acido ---> Sal + Agua


def react(compounds):
    compounds = get_compounds(compounds)
    compoundsType = get_reaction_type(compounds)

    for i in range(0, len(reactions)):
        reaction = reactions[i]
        if str(type(reaction)) == "<class 'list'>":
            if reaction == compoundsType or ((str(reaction[0]) in str(compoundsType[0])) and (str(reaction[1]) in str(compoundsType[1]))):
                reactionType = i+1
                break

        else:
            reaction_1 = reaction[0]
            reaction_2 = reaction[1]

            if ((str(reaction_1[0]) in str(compoundsType[0])) and (str(reaction_1[1]) in str(compoundsType[1]))) or ((str(reaction_2[0]) in str(compoundsType[0])) and (str(reaction_2[1]) in str(compoundsType[1]))):
                reactionType = i+1
                break
    else:
        reactionType = "No es una reaccion organica"

    print(compoundsType, reaction)
    print(reactionType)

    products = get_products(compounds, reactionType)

    results = []
    if type(products) == str:
        if " + " in products:
            comps = products.split(" + ")
            for comp in comps:
                result = {
                    "formula": comp,
                    "properties": get_compound_name(comp)
                }
                results.append(result)
        else:
            result = {
                "formula": products,
                "properties": get_compound_name(products)
            }
            results.append(result)
    else:
        for product in products:
            if " + " in product:
                comps = product.split(" + ")
                for comp in comps:
                    result = {
                        "formula": comp,
                        "properties": get_compound_name(comp)
                    }
                    results.append(result)
            else:
                result = {
                    "formula": product,
                    "properties": get_compound_name(product)
                }
                results.append(result)

    return results


def get_products(compounds, reactionType):
    if reactionType == 1:  # Hidruro metalico
        metal = get_plain_formula(compounds[0].formula)

        if type(oxidation_numbers[metal]) == int:
            products = metal + "H" + \
                str(oxidation_numbers[metal]
                    if oxidation_numbers[metal] != 1 else "")
        else:
            products = set()
            for ox_n in oxidation_numbers[metal]:
                products.add(metal + "H" +
                             str(ox_n if ox_n != 1 else ""))
        return products
    elif reactionType == 2:  # Hidracido
        non_metal = get_plain_formula(compounds[0].formula)

        ox_n = oxidation_numbers[non_metal][0]

        products = "H" + \
            str(abs(ox_n) if abs(ox_n) !=
                1 else "") + non_metal

        return products
    elif reactionType == 3:  # Oxido metalico
        metal = get_plain_formula(compounds[0].formula)

        ox_numbers = oxidation_numbers[metal]

        if type(oxidation_numbers[metal]) == int:

            subindexes = get_subindexes(oxidation_numbers[metal], -2)
            products = metal + subindexes[0] + "O" + subindexes[1]

        else:
            products = set()
            for ox_n in ox_numbers:
                subindexes = get_subindexes(ox_n, -2)
                product = metal + subindexes[0] + "O" + subindexes[1]
                products.add(product)

        return products
    elif reactionType == 4:  # Anhidrido
        non_metal = get_plain_formula(compounds[0].formula)

        ox_numbers = oxidation_numbers[non_metal]

        if type(oxidation_numbers[non_metal]) == int:

            subindexes = get_subindexes(oxidation_numbers[non_metal], -2)
            products = non_metal + subindexes[0] + "O" + subindexes[1]
        else:
            products = set()

            for i in range(0, len(ox_numbers)):
                subindexes = get_subindexes(ox_numbers[i], -2)
                product = non_metal + subindexes[0] + "O" + subindexes[1]
                products.add(product)

        return products
    elif reactionType == 5:  # Hidroxido + H2
        metal_a = get_plain_formula(compounds[0].formula)

        ox_numbers = oxidation_numbers[metal_a]

        if type(oxidation_numbers[metal_a]) == int:

            products = metal_a + \
                "(OH)" + (str(oxidation_numbers[metal_a])
                          if oxidation_numbers[metal_a] != 1 else "") + " + H2"

        else:
            products = set()

            for i in range(0, len(ox_numbers)):
                product = metal_a + \
                    "(OH)" + (str(oxidation_numbers[metal_a][i])
                              if oxidation_numbers[metal_a] != 1 else "") + " + H2"
                products.add(product)

        return products
    elif reactionType == 6:  # Hidroxido
        metal_ox = get_plain_formula(compounds[0].formula)[
            0:get_plain_formula(compounds[0].formula).index("O")]

        metal_ox = ''.join(i for i in metal_ox if not i.isdigit())
        ox_numbers = oxidation_numbers[metal_ox]

        if type(oxidation_numbers[metal_ox]) == int:

            if oxidation_numbers[metal_ox] != 1:
                products = metal_ox + "(OH)" + str(oxidation_numbers[metal_ox])
            else:
                products = metal_ox + "OH"



        else:
            products = set()

            for i in range(0, len(ox_numbers)):
                product = metal_ox + "(OH)" + (str(oxidation_numbers[metal_ox][i])
                                               if oxidation_numbers[metal_ox] != 1 else "")

                if oxidation_numbers[metal_ox][i] != 1:
                    products = metal_ox + "(OH)" + str(oxidation_numbers[metal_ox][i])
                else:
                    products = metal_ox + "OH"
                
                products.add(product)

        return products
    elif reactionType == 7:  # Oxoacido
        non_metal = get_plain_formula(compounds[0].formula)[0:get_plain_formula(compounds[0].formula).index("O")]

        non_metal = ''.join(i for i in non_metal if not i.isdigit())
        print(non_metal)

        ox_numbers = oxidation_numbers[non_metal]

        products = set()

        for i in range(1, len(ox_numbers)):

            nm_subindex = int((ox_numbers[i] + 2)/2)

            product = "H" + str(get_negative(ox_numbers)) + \
                non_metal + "O" + str(nm_subindex)
            products.add(product)

        return products
    elif reactionType == 8:  # Sal binaria
        metal = get_plain_formula(compounds[0].formula)
        non_metal = get_plain_formula(compounds[1].formula)

        metal = ''.join(i for i in metal if not i.isdigit())
        non_metal = ''.join(i for i in non_metal if not i.isdigit())
        #
        print(metal, non_metal)

        metal_ox_numbers = oxidation_numbers[metal]
        nonmetal_ox_numbers = oxidation_numbers[non_metal]

        print(metal_ox_numbers, str(get_negative(nonmetal_ox_numbers)))

        if type(oxidation_numbers[metal]) == int:

            subindexes = get_subindexes(
                metal_ox_numbers, get_negative(nonmetal_ox_numbers))
            products = metal + subindexes[0] + non_metal + subindexes[1]
        else:
            products = set()

            for i in range(0, len(metal_ox_numbers)):
                subindexes = get_subindexes(
                    metal_ox_numbers[i], str(get_negative(nonmetal_ox_numbers)))
                product = metal + subindexes[0] + non_metal + subindexes[1]
                products.add(product)
        return products
    elif reactionType == 9:  # Sal + Hidrogeno
        metal = get_plain_formula(compounds[0].formula)
        acid = get_plain_formula(compounds[1].formula)

        non_metal = acid.replace('H', '')
        non_metal = non_metal.replace('O', '')
        non_metal = ''.join(i for i in non_metal if not i.isdigit())

        print(metal, acid, non_metal)

        metal_ox_numbers = oxidation_numbers[metal]
        nonmetal_ox_numbers = oxidation_numbers[non_metal]

        print(metal_ox_numbers, str(get_negative(nonmetal_ox_numbers)))

        if type(oxidation_numbers[metal]) == int:

            subindexes = get_subindexes(
                metal_ox_numbers, get_negative(nonmetal_ox_numbers))
            products = metal + subindexes[0] + \
                non_metal + subindexes[1] + " + H2"
        else:
            products = set()

            for i in range(0, len(metal_ox_numbers)):
                subindexes = get_subindexes(
                    metal_ox_numbers[i], str(get_negative(nonmetal_ox_numbers)))
                product = metal + subindexes[0] + non_metal + subindexes[1]
                products.add(product + " + H2")
        return products
    elif reactionType == 10:  # Sal + Agua
        hidrox = get_plain_formula(compounds[0].formula)
        acid = get_plain_formula(compounds[1].formula)

        metal = hidrox.replace('O', '')
        metal = metal.replace('H', '')
        metal = ''.join(i for i in metal if not i.isdigit())

        non_metal = acid.replace('H', '')
        non_metal = non_metal.replace('O', '')
        non_metal = ''.join(i for i in non_metal if not i.isdigit())

        metal_ox_numbers = oxidation_numbers[metal]

        if "O" in acid:
            oxygen = acid[acid.index("O"): len(acid)]

            product = metal + str(
                compounds[1].occurences['H'] if compounds[1].occurences['H'] != 1 else "") + "(" + non_metal + str(
                compounds[1].occurences[non_metal] if compounds[1].occurences[non_metal] != 1 else "") + oxygen + ")"

            if type(metal_ox_numbers) == int:

                if compounds[1].occurences['H'] != metal_ox_numbers:
                    products = product + \
                        (str(metal_ox_numbers) if metal_ox_numbers != 1 else "")
                else:
                    product = metal + non_metal + oxygen
                    products = product + " + H2O"
            else:
                products = set()
                for ox in metal_ox_numbers:
                    products.append(product + (ox if ox != 1 else ""))

            return products
        else:
            oxygen = ""

        print(metal, acid, non_metal, oxygen)

        nonmetal_ox_numbers = oxidation_numbers[non_metal]

        if type(metal_ox_numbers) == int:
            subindexes = get_subindexes(
                metal_ox_numbers, get_negative(nonmetal_ox_numbers))

            if subindexes[1] == 1:
                product = metal + subindexes[0] + non_metal + oxygen
            elif subindexes[0] == 1:
                product = metal + non_metal + subindexes[1] + oxygen
            elif subindexes[1] == subindexes[0]:
                product = metal + non_metal + oxygen
            else:
                product = metal + \
                    subindexes[0] + "(" + non_metal + \
                    oxygen + ")" + subindexes[1]

            if oxygen == "":
                product = product.replace('(', '')
                product = product.replace(')', '')

            products = product + " + H2O"
        else:
            products = set()

            for i in range(0, len(metal_ox_numbers)):
                subindexes = get_subindexes(
                    metal_ox_numbers[i], get_negative(nonmetal_ox_numbers))

                if subindexes[1] == 1:
                    product = metal + subindexes[0] + \
                        non_metal + subindexes[1] + oxygen
                else:
                    product = metal + \
                        subindexes[0] + "(" + non_metal + \
                        oxygen + ")" + subindexes[1]
                products = product + " + H2O"

                products.add(product + oxygen + " + H2O")
        return products


def get_compound_name(compound):
    if compound != "H2O" and compound != "O2" and compound != "H2":
        response = requests.get(
            "https://www.formulacionquimica.com/" + compound)

        print("Compound: ", compound)

        soup = BeautifulSoup(response.content, "html.parser")

        results = soup.find_all("p")

        properties = []

        for i in range(3, 7):
            r = results[i]
            htmlElement = BeautifulSoup(
                str(r), 'html.parser')
            properties.append(htmlElement.get_text()[
                              htmlElement.get_text().index(":") + 2: len(htmlElement.get_text())])

        properties_dict = {
            "nomenclatura_sistematica": properties[0],
            "nomenclatura_stock": properties[1],
            "nomenclatura_tradicional": properties[2],
            "tipo_compuesto": properties[3]}

        return(properties_dict)


def get_negative(num_list):
    num = [item for item in num_list if item <= 0]
    return abs(num[0])


def get_subindexes(a, b):
    a = abs(a)
    b = abs(b)
    mcd_r = mcd(a, b)

    a_subindex = int(a/mcd_r)
    b_subindex = int(b/mcd_r)

    if a_subindex == 1:
        a_subindex = ""
    if b_subindex == 1:
        b_subindex = ""

    return [str(b_subindex), str(a_subindex)]


def mcd(a, b):
    if b == 0:
        return a
    return mcd(b, a % b)


def get_reaction_type(compounds):
    types = []
    for i in range(0, 2):
        types.append(get_compound_type(compounds[i]))
    return types


def get_compounds(compounds):
    compounds = compounds.split(" + ")

    compounds = map(lambda comp: Compound(comp), compounds)
    return list(compounds)


def get_compound_type(compound):

    plain_formula = get_plain_formula(compound.formula)

    # is hidroxyd?
    comps = list(compound.occurences.keys())

    if len(list(compound.occurences)) == 3 and "H" in plain_formula and "O" in plain_formula:
        el = plain_formula.replace('H', '')
        el = el.replace('O', '')
        el = ''.join(i for i in el if not i.isdigit())

        element = Element(el)

        if element.properties["Metal"]:
            plain_formula = el + \
                "(OH)" + str(compound.occurences['H']
                             ) if compound.occurences['H'] > 1 else el + "OH"

    ############################################################################################

    print(plain_formula)

    if len(compound.occurences) == 1:
        if plain_formula == "O2":
            compoundType = "Oxygen"
        elif plain_formula == "H2":
            compoundType = "Hydrogen"
        else:
            element = Element(list(compound.occurences.keys())[0])
            compoundType = (
                "Metal-" + str(element.properties["Group"])) if element.properties["Metal"] else "Nm/Mll-" + str(element.properties["Group"])

    else:
        if plain_formula != "H2O":
            response = requests.get(
                "https://www.formulacionquimica.com/" + plain_formula)

            soup = BeautifulSoup(response.content, "html.parser")

            results = soup.find_all("p")

            for i in range(0, len(results)):
                if results[i].find("a") != None:
                    results = str(results[i].find("a"))
                    break

            htmlElement = BeautifulSoup(
                results, 'html.parser')
            tag = htmlElement.a

            compoundType = str(tag.string)

            if "ácido" in compoundType:
                compoundType = "Acid-"
            elif "óxido metálico" in compoundType:
                compoundType = "MetalOxide-"
            elif "anhídrido" in compoundType:
                compoundType = "Anhydride-"
            elif "hidróxido" in compoundType:
                compoundType = "Hydroxide-"
        else:
            compoundType = "Water"
    return compoundType


def get_plain_formula(sub_formula):
    subindexes = ["₁", "₂", "₃", "₄", "₅", "₆", "₇", "₈", "₉"]

    plain_formula = sub_formula

    for i in range(0, 8):
        plain_formula = plain_formula.replace(
            subindexes[i], (str(i+1) if i != 0 else ""))

    return plain_formula


def parse_ansi(text):
    for i in range(0, 5):
        text = text.replace(accent_letters[list(accent_letters.keys())[
            i]], list(accent_letters.keys())[i])
    return text
