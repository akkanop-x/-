import json
import re
import pubchempy as pcp
from chempy import balance_stoichiometry

with open('data.json', 'r') as f:
    data = json.load(f)

def showMenu():
    ("\nตัวเลือก:")

    print("1. ตารางธาตุ")
    print("2. ค้นหาธาตุ")
    print("3. การอ่านชื่อธาตุและสารประกอบ")
    print("4. ชื่อสารเคมี")
    print("5. วิธีการจัดเรียงอิเล็กตรอน")
    print("6. การจัดเรียงอิเล็กตรอน")
    print("7. วิธีการดุลสมการเคมี")
    print("8. ดุลสมการเคมี")
    print("0. ออกจากเมนู")

def th_category(category):
    category_mapping = {
        'diatomic nonmetal': 'อโลหะ',
        'noble gas': 'ก๊าซเฉื่อย',
        'alkali metal': 'โลหะแอลคาไลน์เอิร์ท',
        'alkaline earth metal': 'โลหะแอลคาไลน์เอิร์ท',
        'metalloid': 'ธาตุกึ่งโลหะ',
        'polyatomic nonmetal': 'ธาตุอโลหะ',
        'post-transition metal': 'โลหะหลังทรานซิชัน',
        'transition metal': 'โลหะทรานซิชัน',
        'lanthanide': 'แลนทาไนด์',
        'actinide': 'แอกทิไนด์',
        'unknown, probably transition metal': 'ไม่ทราบ, อาจจะเป็นโลหะทรานซิชัน',
        'unknown, probably post-transition metal': 'ไม่ทราบ, อาจจะเป็นโลหะหลังทรานซิชัน',
        'unknown, probably metalloid': 'ไม่ทราบ, อาจจะเป็นธาตุกึ่งโลหะ',
        'unknown, predicted to be noble gas': 'ไม่ทราบ, อาจจะเป็นก๊าซเฉื่อย',
        'unknown, but predicted to be an alkali metal': 'ไม่ทราบ, อาจจะเป็นโลหะแอลคาไลน์เอิร์ท'
    }
    return category_mapping.get(category, 'ไม่ทราบ')

def chemical_equations(equation_str):
    reactants, products = re.split(r'=|->', equation_str)

    reactants = reactants.strip().split('+')
    products = products.strip().split('+')

    reactants = [reactant.strip() for reactant in reactants]
    products = [product.strip() for product in products]

    balanced_reactants, balanced_products = balance_stoichiometry(reactants, products)

    balanced_equation = ' + '.join([f'{coef}{species}' for species, coef in balanced_reactants.items()]) + ' -> ' + ' + '.join([f'{coef}{species}' for species, coef in balanced_products.items()])
    return balanced_equation

def search_element(query):
    found_elements = []

    query = query.lower()
    
    for element in data['elements']:
        element_name = element['name']

        if query in element_name:
            element_dict = {
                'ชื่อ': element['name'],
                'เลขอะตอม': element['number'],
                'มวลอะตอม': element['atomic_mass'],
                'หมวดหมู่': th_category(element['category']),
                'ระดับ': element['period'],
                'สัญลักษณ์': element['symbol'],
            }
            found_elements.append(element_dict)

    return found_elements

def get_atomic_number(element_name):
    for element in data['elements']:
        if element['name'] == element_name.capitalize():
            return element['number']
    return None

def electron_configuration(atomic_number):
    electron_config = ""
    electron_count = atomic_number

    orbitals = [
        ('1s', 2),
        ('2s', 2), ('2p', 6),
        ('3s', 2), ('3p', 6), ('3d', 10),
        ('4s', 2), ('4p', 6), ('4d', 10), ('4f', 14),
        ('5s', 2), ('5p', 6), ('5d', 10), ('5f', 14),
        ('6s', 2), ('6p', 6), ('6d', 10),
        ('7s', 2), ('7p', 6),
    ]

    for orbital, max_electrons in orbitals:
        if electron_count == 0:
            break
        if electron_count >= max_electrons:
            electron_config += f"{orbital}{max_electrons} "
            electron_count -= max_electrons
        else:
            electron_config += f"{orbital}{electron_count} "
            electron_count = 0

    return electron_config.strip()

while True:
    showMenu()
    choice = input("\nPlease Select: ")

    if choice == "1": # ตารางธาตุ
        for element in data['elements']:
            print({
                'ชื่อ': element['name'],
                'เลขอะตอม': element['number'],
                'มวลอะตอม': element['atomic_mass'],
                'หมวดหมู่': th_category(element['category']),
                'ระดับ': element['period'],
                'สัญลักษณ์': element['symbol'],
            })
        continue_option = input("กด Enter เพื่อดำเนินการต่อ...")
        continue
    
    elif choice == "2": # ค้นหาธาตุ
        element_query = input("ค้นหาธาตุ: ")
        found_elements = search_element(element_query)
        if found_elements:
            print("ผลการค้นหา:")
            for element in found_elements:
                print(json.dumps(element, ensure_ascii=False, indent=2))
        else:
            print(f"ไม่พบธาตุที่ตรงกับคำค้นหา '{element_query}'")
                
        continue_option = input("กด Enter เพื่อดำเนินการต่อ...")
        continue

    elif choice == "3": # การอ่านชื่อธาตุและสารประกอบ
        chemical_formula = input("ชื่อสารประกอบ: ")
        try:
            compounds = pcp.get_compounds(chemical_formula, 'formula')
            
            if compounds:
                compound = compounds[0]
                print({
                    'ชื่อ': compound.iupac_name,
                    'องค์ประกอบ': compound.elements,
                    'สูตรโมเลกุล': compound.molecular_formula,
                    'น้ำหนักโมเลกุล': compound.molecular_weight,
                })
            else:
                print("No compounds found with the formula:", chemical_formula)

        except pcp.PubChemHTTPError as e:
            print("Error:", e)
        continue_option = input("กด Enter เพื่อดำเนินการต่อ...")
        continue

    elif choice == "4": # ชื่อสารเคมี
        chemical_formula = input("ชื่อสารประกอบ: ")
        try:
            compounds = pcp.get_compounds(chemical_formula, 'formula')
            
            if compounds:
                compound = compounds[0]
                print({
                    'ชื่อ': compound.iupac_name,
                })
            else:
                print("No compounds found with the formula:", chemical_formula)

        except pcp.PubChemHTTPError as e:
            print("Error:", e)
        continue_option = input("กด Enter เพื่อดำเนินการต่อ...")
        continue

    elif choice == "5": # วิธีการจัดเรียงอิเล็กตรอน
        print(" \
            == การจัดเรียงอิเล็กตรอน แบบใช้หลัก  2  8  18  32  (สำหรับธาตุหมู่ 1A ถึงหมู่ 8A) ==\n\n\
            1.ให้จัดอิเล็กตรอนทั้งหมด โดยเรียงจำนวนตามขั้นบันไดขึ้นด้านบน\n\
            2.เมื่อไม่สามารถจัดอิเล็กตรอนขั้นถัดไป ให้จัดอิเล็กตรอนในบันไดขั้นเดิมได้ 1 ครั้งหรือขั้นที่ลดลงมา\n\
            โดยอิเล็กตรอนหลักสุดท้ายจะต้องมีจำนวนอิเล็กตรอนไม่เกิน 8 ตัว เสมอ\n\
            * เลขหมู่ จะตรงกับเลขหลักสุดท้ายของการจัดเรียงอิเล็กตรอน ดังนั้น ธาตุที่อยู่หมู่เดียวกันจะมีเวเลนซ์อิเล็กตรอนเท่ากัน\n\
            * จำนวนหลักของระดับพลังงาน จะตรงกับเลขของคาบ ดังนั้น ธาตุในคาบเดียวกันจะมีจำนวนระดับพลังงานเท่ากัน\n\
            ")
        continue_option = input("กด Enter เพื่อดำเนินการต่อ...")
        continue

    elif choice == "6": # การจัดเรียงอิเล็กตรอน
        element_name = input("กรอกธาตุตัวที่ต้องการให้ระบบจัดเรียง: ")
        atomic_number = get_atomic_number(element_name)

        if atomic_number is not None:
            print(electron_configuration(atomic_number))
        else:
            print(f"Element {element_name} not found in the data.")

        continue_option = input("กด Enter เพื่อดำเนินการต่อ...")
        continue

    elif choice == "7": # วิธีการดุลสมการเคมี
        print("\
            วิธีดุลสมการเคมี\n\n\
            1.เขียนสมการเคมีให้ถูกต้องตามหลักการเขียนสมการเคมี\n\
            2.พิจารณาธาตุที่ปรากฏอยู่ในสมการเคมีทั้งหมด\n\
            3.เริ่มต้นดุลธาตุที่ปรากฏในสมการเคมีเพียงธาตุเดียว โดยพยายามหาจำนวนสัมประสิทธิ์ที่เหมาะสมเพื่อให้จำนวนอะตอมของธาตุนั้นๆ ทั้งสองด้านของสมการเท่ากัน\n\
            4.เมื่อดุลธาตุใดธาตุหนึ่งได้แล้ว ให้พิจารณาธาตุอื่นๆ ที่เหลือ และดุลธาตุเหล่านั้นต่อไปตามลำดับ\n\
            5.ตรวจสอบสมการเคมีอีกครั้งเพื่อให้แน่ใจว่าจำนวนอะตอมของธาตุทุกชนิดทั้งสองด้านของสมการเท่ากัน\n\
        ")
        continue_option = input("กด Enter เพื่อดำเนินการต่อ...")
        continue

    elif choice == "8": # ดุลสมการเคมี
        equation = input('Equations ( H2 + O2 = H2O, eg. ): ')
        result = chemical_equations(equation)
        print("Balanced: ", result)
        
        continue_option = input("กด Enter เพื่อดำเนินการต่อ...")
        continue

    elif choice == "0": # Exit 
        break
    else:
        print("Invalid choice. Please select a valid option.")
