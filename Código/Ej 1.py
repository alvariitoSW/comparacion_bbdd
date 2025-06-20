import os
import ujson # Versión rápida de json - "orjson" es mejor, pero no es del todo compatible
import csv
import random
from tqdm import tqdm
from faker import Faker
from faker.providers import BaseProvider
import multiprocessing
from multiprocessing import freeze_support, Manager
import unidecode

# Clase con funcionalidad extra de faker para usuarios
class CustomUserProviders(BaseProvider):
    # Últimas letras de los DNIs
    __letters = "TRWAGMYFPDXBNJZSQVHLCKE"
    __provinces = [
        "Álava", "Albacete", "Alicante", "Almería", "Ávila", "Badajoz",
        "Baleares", "Barcelona", "Burgos", "Cáceres", "Cádiz", "Castellón",
        "Ciudad Real", "Córdoba", "La Coruña", "Cuenca", "Gerona", "Granada",
        "Guadalajara", "Guipúzcoa", "Huelva", "Huesca", "Jaén", "León",
        "Lérida", "La Rioja", "Lugo", "Madrid", "Málaga", "Murcia", "Navarra",
        "Orense", "Asturias", "Palencia", "Las Palmas", "Pontevedra", "Salamanca",
        "Santa Cruz de Tenerife", "Cantabria", "Segovia", "Sevilla", "Soria",
        "Tarragona", "Teruel", "Toledo", "Valencia", "Valladolid", "Vizcaya",
        "Zamora", "Zaragoza", "Ceuta", "Melilla"
    ]
    # Lista con parejas (ciudad, provincia) sacados del dataset
    __cities = []
    # Prefijos telefónicos correspondietes a la lista de provincias
    __prefixes = [
        "945", "967", "96", "950", "920", "924",
        "971", "93", "947", "927", "956", "964",
        "926", "957", "981", "969", "972", "958",
        "949", "943", "959", "974", "953", "987",
        "973", "941", "982", "91", "952", "968", "948",
        "988", "98", "979", "928", "986", "923",
        "922", "942", "921", "95", "975",
        "977", "978", "925", "96", "983", "944",
        "980", "976", "956", "952"
    ]

    def __init__(self, generator) -> None:
        super().__init__(generator)
        with open('datasets/codigos_postales_municipios.csv', mode='r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader) # Saltarse el header
            for row in reader:
                self.__cities.append((row[0], row[2]))

    def __dni_number(self, start, end) -> int:
        return base_fake.unique.random_int(min=start, max=end)

    def __dni_control_letter(self, num):
        return self.__letters[num % 23]

    def dni(self, start=111111, end=99999999) -> str:
        num = self.__dni_number(start, end)
        control = self.__dni_control_letter(num)
        return f'{num:08d}{control}'

    def email_from_name(self, name, domain) -> str:
        # Formatos en los que un email puede
        formats = [
            # Formatos creados manualmente
            lambda a, b, c: f"{a}{b}{c}",
            lambda a, b, c: f"{a}{b}",
            lambda a, b, c: f"{a}{b}{random.randint(1, 99)}",
            lambda a, b, c: f"{b}{c}",
            lambda a, b, c: f"{a[0]}{b}{c}",
            lambda a, b, c: f"{a[0]}{b}",
            lambda a, b, c: f"{a}.{b}{c}",
            lambda a, b, c: f"{a}.{b}",
            lambda a, b, c: f"{a}.{b}.{c}",
            lambda a, b, c: f"{a}_{b}",
            lambda a, b, c: f"{b}_{c}",
            lambda a, b, c: f"{b}_{c}{random.randint(1, 99)}",

            # Formatos generados por IA
            lambda a, b, c: f"{a[0]}{b[0]}{c}",
            lambda a, b, c: f"{a}{c}",
            lambda a, b, c: f"{a[0]}{c}",
            lambda a, b, c: f"{a}{b[0]}{c[0]}",
            lambda a, b, c: f"{a}_{b}_{c}",
            lambda a, b, c: f"{a[0]}_{b}_{c}",
            lambda a, b, c: f"{a}.{c}",
            lambda a, b, c: f"{b}.{a[0]}{c[0]}",
            lambda a, b, c: f"{a}{b[:3]}{c[:3]}",
            lambda a, b, c: f"{a[:3]}{b[:3]}{c[:3]}",
            lambda a, b, c: f"{a}-{b}-{c}",
            lambda a, b, c: f"{a[0]}{b}-{c}",
            lambda a, b, c: f"{a}{b}{random.randint(100, 999)}",
            lambda a, b, c: f"{a[0]}{b[0]}{c[0]}{random.randint(10, 99)}",
            lambda a, b, c: f"{a}.{b[0]}{c[0]}",
            lambda a, b, c: f"{b[:4]}{a[0]}{c[0]}",
            lambda a, b, c: f"{c}{a[0]}{b[0]}",
            lambda a, b, c: f"{a}{b[:2]}{c[:2]}",
            lambda a, b, c: f"{a[:2]}.{b[:2]}.{c[:2]}",
            lambda a, b, c: f"{a}{b[0]}_{c[0]}",
            lambda a, b, c: f"{a[:2]}{b[:2]}{c[:2]}{random.randint(1, 999)}",
            lambda a, b, c: f"{a[0]}{b[0]}{c[0]}.{random.randint(1, 99)}",
            lambda a, b, c: f"{c[:3]}.{a[0]}{b[0]}",
            lambda a, b, c: f"{a}-{b[0]}-{c[0]}",
            lambda a, b, c: f"{b[:3]}{c[:3]}.{a[0]}"
        ]

        name_split = unidecode.unidecode(name).lower().split(" ") # Se limpian tildes y eñes ya que no están permitidas en correos
        return random.choice(formats)(name_split[0], name_split[1], name_split[2]) + "@" + domain

    def mobile_phone(self) -> str:
        # Todos los móviles empiezan con 6 o 7
        return "(+34) " + str(random.randint(6, 7)) + str(random.randint(0, 99999999)).zfill(8)

    def landline_phone(self, post_code) -> str:
        # El predijo se selecciona basado en la provincia
        prefix = self.__prefixes[int(post_code[:2]) - 1]
        return prefix + str(random.randint(0, (999999 if len(prefix) == 3 else 9999999))).zfill(6 if len(prefix) == 3 else 7)

    def location_data(self) -> list:
        city = random.choice(self.__cities)
        return [city[1], city[0], self.__provinces[int(city[0][:2]) - 1]]

# Clase con funcionalidad extra de faker para coches
class CustomCarProviders(BaseProvider):
    # Lista con la última matrícula de cada año https://www.seisenlinea.com/edad-matriculas/
    __registration_plate_periods = [
        "BDR", "BRT", "CDC", "CRC", "DFF", "DVB", "FKC", "FYY",
        "GKH", "GSR", "HBG", "HHT", "HNK", "HVF", "JBY", "JKZ",
        "JVZ", "KGN", "KSS", "LDR", "LMC", "LVV", "MDD", "MMN"
    ]
    # Lista con modelos y fabricantes
    __car_list = [
        ('Volkswagen', [('Golf', 'Compacto'), ('Passat', 'Sedán'), ('Tiguan', 'SUV')]),
        ('BMW', [('Serie 1', 'Sedán'), ('Serie 3', 'Sedán'), ('X5', 'SUV')]),
        ('Audi', [('A3', 'Sedán'), ('A4', 'Sedán'), ('Q7', 'SUV')]),
        ('Mercedes-Benz', [('Clase A', 'Sedán'), ('Clase C', 'Sedán'), ('GLA', 'SUV')]),
        ('Ford', [('Fiesta', 'Compacto'), ('Focus', 'Compacto'), ('Kuga', 'SUV')]),
        ('Renault', [('Clio', 'Compacto'), ('Mégane', 'Compacto'), ('Koleos', 'SUV')]),
        ('Peugeot', [('208', 'Compacto'), ('308', 'Compacto'), ('3008', 'SUV')]),
        ('Opel', [('Astra', 'Compacto'), ('Insignia', 'Sedán'), ('Mokka', 'SUV')]),
        ('Volkswagen', [('Golf', 'Compacto'), ('Passat', 'Sedán'), ('Tiguan', 'SUV')]),
        ('Skoda', [('Octavia', 'Compacto'), ('Karoq', 'SUV'), ('Superb', 'Sedán')]),
        ('Seat', [('Ibiza', 'Compacto'), ('Leon', 'Compacto'), ('Tarraco', 'SUV')]),
        ('Nissan', [('Juke', 'SUV'), ('Qashqai', 'SUV'), ('Altima', 'Sedán')]),
        ('Hyundai', [('i20', 'Compacto'), ('i30', 'Compacto'), ('Tucson', 'SUV')]),
        ('Kia', [('Rio', 'Compacto'), ('Ceed', 'Compacto'), ('Sportage', 'SUV')]),
        ('Citroën', [('C3', 'Compacto'), ('C4', 'Compacto'), ('C5 Aircross', 'SUV')]),
        ('Jaguar', [('XE', 'Sedán'), ('XF', 'Sedán'), ('F-Pace', 'SUV')]),
        ('Land Rover', [('Discovery Sport', 'SUV'), ('Defender', 'SUV'), ('Range Rover', 'SUV')]),
        ('Maserati', [('Ghibli', 'Sedán'), ('Levante', 'SUV'), ('Quattroporte', 'Sedán')]),
        ('Alfa Romeo', [('Giulia', 'Sedán'), ('Stelvio', 'SUV'), ('159', 'Sedán')]),
        ('Ferrari', [('488', 'Deportivo'), ('Roma', 'Deportivo'), ('Portofino', 'Deportivo')])
    ]
    # Códigos de matrícula por provincia
    __province_codes = [
        "C", "VI", "AB", "A", "AL", "O", "AV", "BA",
        "B", "CC", "CA", "S", "CS", "CE", "CR", "CO",
        "CU", "GI", "GR", "GU", "SS", "H", "HU", "IB",
        "J", "LO", "GC", "LE", "L", "LU", "M", "MA",
        "ML", "MU", "NA", "OU", "PO", "SA", "TF", "SG",
        "SE", "SO", "T", "TE", "TO", "V", "VA", "BI",
        "ZA", "Z"
    ]

    def car_model_and_category(self) -> list[str]:
        [car, models] = random.choice(self.__car_list)
        [model, category] = random.choice(models)

        return [car, model, category]

    def __get_current_registration_plate(self, start, end) -> str:
        # Matrícula generada con letras en un intervalo para evitar colisiones entre threads
        return str(random.randint(0, 9999)).zfill(4) + " " + random.choice("BCDFGHJKLM") + self.__get_base_letters(start, end)

    def __get_old_registration_plate(self, start, end) -> str:
        # Matrícula generada con letras en un intervalo para evitar colisiones entre threads
        return random.choice(self.__province_codes) + " " + str(random.randint(0, 9999)).zfill(4) + " " + self.__get_base_letters(start, end)

    def __get_base_letters(self, start, end):
        letters = "ABCDEFGHIJKLMNOPRSTUVWXYZ"
        base = random.randint(start, end)
        first_letter_index, second_letter_index = divmod(base, 25)
        return letters[first_letter_index] + letters[second_letter_index]

    def get_registration_plate(self, start=0, end=624) -> str:
        # Genera una matrícula antigua con un 15% de probabilidad
        if random.random() < 0.15:
            return self.__get_old_registration_plate(start, end)
        return self.__get_current_registration_plate(start, end)

    def registration_period(self, plate) -> None:
        plate_aux = plate.split(" ")[1]

        # Si la matrícula es moderna se selecciona su año correspondiente
        year = random.randint(1974, 2000)
        i = 0
        while (i < 24 and plate_aux > self.__registration_plate_periods[i]):
            i += 1
            year = 2000 + i

        return year

    def generate_vin(self, start=0, end=624):
        # Vin generado con letras en un intervalo para evitar colisiones entre threads
        letters = "ABCDEFGHIJKLMNOPRSTUVWXYZ0123456789"
        vin = ''.join(random.choices(letters, k=15)) + self.__get_base_letters(start, end)
        return vin

base_fake = Faker('es_ES')
base_fake.add_provider(CustomUserProviders)
base_fake.add_provider(CustomCarProviders)

###########################################################

def get_user_entry(start_dni, end_dni, fake):
    dni = fake.unique.dni(start_dni, end_dni)
    
    name = f"{fake.first_name()} {fake.last_name()} {fake.last_name()}"
    [city, post_code, province] = fake.location_data()

    return {
        "name": name,
        "dni": dni,
        "email": fake.email_from_name(name, fake.free_email_domain()),
        "mobile_phone": fake.unique.mobile_phone(),
        "landline_phone": fake.unique.landline_phone(post_code),
        "address": fake.address().split("\n")[0].strip(),
        "city": city,
        "post_code": post_code,
        "province": province
    }

def get_user_entry_keys():
    return [
        "name", "dni", "email", "mobile_phone", "landline_phone",
        "address", "city", "post_code", "province"
    ]

def get_car_entry(dnis, start_plate_vin, end_plate_vin, fake):
    vin = fake.unique.generate_vin(start_plate_vin, end_plate_vin)
    [maker, model, category] = fake.car_model_and_category()
    plate = fake.unique.get_registration_plate(start_plate_vin, end_plate_vin)
    year = fake.registration_period(plate)

    return {
        "plate": plate,
        "dni": random.choice(dnis),
        "vin": vin,
        "year": year,
        "maker": maker,
        "model": model,
        "category": category
    }

def get_car_entry_keys():
    return [
        "plate", "dni", "vin", "year",
        "maker", "model", "category"
    ]

###########################################################

def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def dump_json_chunk(data, directory, output_filename, lock=None):
    try:
        output_path = os.path.join(directory, output_filename)
        
        # Evitar que se sobreescriban datos
        if lock:
            lock.acquire()
        
        # Guardar la lista sin los corchetes, que se añaden automáticamente al principio y al final del archivo
        with open(output_path, 'a', encoding='utf-8') as file:
            json_str = ujson.dumps(data, ensure_ascii=False, indent=4)
            json_str_no_brackets = "\t" + json_str[1:-1].strip()
            file.write(json_str_no_brackets + ",\n")
        
        if lock:
            lock.release()
    except Exception as e:
        print(f"An error occurred: {e}")

def write_json(output_filename, txt, lock=None, new=False, rm=None):
    # Evitar que se sobreescriban datos
    if lock:
        lock.acquire()        

    if rm:
        with open(output_filename, 'rb+') as file:
            file.seek(-rm, os.SEEK_END)
            file.truncate()
    
    with open(output_filename, 'w' if new else 'a', encoding='utf-8') as file:
        file.write(txt)
    
    if lock:
        lock.release()

def dump_csv_chunk(data, directory, output_filename, lock=None):
    try:
        output_path = os.path.join(directory, output_filename)

        # Evitar que se sobreescriban datos
        if lock:
            lock.acquire()

        with open(output_path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writerows(data)

        if lock:
            lock.release()
    except Exception as e:
        print(f"An error occurred: {e}")

def initialize_csv_file(output_filename, fieldnames):
    with open(output_filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

###########################################################

def thread_func(args):
    chunk_size, thread_n, num_processes, total_size, file_lock = args
    fake = Faker('es_ES')
    fake.add_provider(CustomUserProviders)
    fake.add_provider(CustomCarProviders)

    users = {}
    cars = []

    # Definir intervalos de DNIs y matrículas para evitar colisiones entre threads
    start_dni = (99999999 // num_processes) * thread_n + 1
    end_dni = (99999999 // num_processes) * (thread_n + 1)

    # Imprimir el progreso de uno de los threads
    if thread_n == 0:
        for _ in tqdm(range(chunk_size), desc=f"Generating users ({total_size:,})"):
            user = get_user_entry(start_dni, end_dni, fake)
            dni = user["dni"]
            users[dni] = user
    else:
        for _ in range(chunk_size):
            user = get_user_entry(start_dni, end_dni, fake)
            dni = user["dni"]
            users[dni] = user

    values = list(users.values())
    dump_json_chunk(values, "results/users/json", f"users_{total_size}.json", file_lock)
    dump_csv_chunk(values, "results/users/csv", f"users_{total_size}.csv", file_lock)

    start_plate_vin = (624 // num_processes) * thread_n
    end_plate_vin = (624 // num_processes) * (thread_n + 1) - 1

    # Imprimir el progreso de uno de los threads
    dnis = list(users.keys())
    if thread_n == 0:
        for _ in tqdm(range(chunk_size), desc=f"Generating cars ({total_size:,})"):
            car = get_car_entry(dnis, start_plate_vin, end_plate_vin, fake)
            users[car["dni"]].setdefault("cars", []).append(car)
            cars.append(car)
    else:
        for _ in range(chunk_size):
            car = get_car_entry(dnis, start_plate_vin, end_plate_vin, fake)
            users[car["dni"]].setdefault("cars", []).append(car)
            cars.append(car)
    del dnis

    dump_json_chunk(cars, "results/cars/json", f"cars_{total_size}.json", file_lock)
    dump_csv_chunk(cars, "results/cars/csv", f"cars_{total_size}.csv", file_lock)

    for car in cars:
        del car["dni"]

    dump_json_chunk(list(users.values()), "results/mix", f"mix_{total_size}.json", file_lock)

def parallel_generate_data_and_save(total_size, num_processes):
    chunk_size = total_size // num_processes
    pool = multiprocessing.Pool(processes=num_processes)
    manager = Manager()
    file_lock = manager.Lock()

    # Iniciar los archivos
    initialize_csv_file(f"results/users/csv/users_{total_size}.csv", get_user_entry_keys())
    write_json(f"results/users/json/users_{total_size}.json", "[\n", file_lock, new=True)
    write_json(f"results/mix/mix_{total_size}.json", "[\n", file_lock, new=True)
    initialize_csv_file(f"results/cars/csv/cars_{total_size}.csv", get_car_entry_keys())
    write_json(f"results/cars/json/cars_{total_size}.json", "[\n", file_lock, new=True)

    # Iniciar los threads
    args = [(chunk_size + (total_size % num_processes) if i == 0 else chunk_size, i, num_processes, total_size, file_lock) for i in range(num_processes)]
    pool.map(thread_func, args)
    pool.close()
    pool.join()

    # Cerrar los json
    write_json(f"results/users/json/users_{total_size}.json", "\n]", file_lock, rm=3)
    write_json(f"results/cars/json/cars_{total_size}.json", "\n]", file_lock, rm=3)
    write_json(f"results/mix/mix_{total_size}.json", "\n]", file_lock, rm=3)

def main():
    # Usar el 75% de los threads del ordenador para evitar que se ralentize en otras tareas
    num_processes = round(multiprocessing.cpu_count() * 0.75)
    print(f"Generating data with {num_processes} threads")

    ensure_directory_exists("results/users/json")
    ensure_directory_exists("results/users/csv")

    ensure_directory_exists("results/mix")
    
    ensure_directory_exists("results/cars/json")
    ensure_directory_exists("results/cars/csv")

    for exp in range(3, 6): # Generar datos de 1000 a 100000
        n = 10**exp
        parallel_generate_data_and_save(n, num_processes)

if __name__ == '__main__':
    freeze_support()
    main()