def recognition_birthday_date(date: str) -> [datetime, None]:
    regex = re.compile(r"(\d\d?).(\d\d?).(\d\d\d\d)")
    if re.findall(regex, date):
        try:
            cal = re.findall(regex, date)
            cal = [int(_) for _ in cal[0][::-1]]
            calendar_date = datetime(*cal)
            logging.debug(f"Встановлена дата народження {datetime}")
        except ValueError:
            logging.error ("Такої дати не існує")
        except:
            logging.error ('Сталася помилка')  
    else:
        logging.error ("Ви ввели дату не за шаблоном")
    return calendar_date

def decorator(func):
    def wraper(date: str):
        if  isinstance(func(date), datetime):
            print(true)
        else:
            return False
    return wraper

date_v = "28-03-1994"

def start():
    @decorator
    recognition_birthday_date(date_v)

print (start())

