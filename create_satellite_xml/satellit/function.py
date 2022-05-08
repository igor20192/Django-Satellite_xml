from cgitb import text
import re
from unicodedata import name
from bs4 import BeautifulSoup
import httpx
import xml.etree.ElementTree as xml
import time
from satellit.models import My_Sat_xml
from zipfile import ZipFile


def beautify_xml(xml_str):
    import xml.dom.minidom

    dom = xml.dom.minidom.parseString(xml_str)
    return dom.toprettyxml()


def zpifile(user_id):
    archive = ZipFile(f"media/satellites{str(user_id)}.zip", mode="w")
    archive.write("media/satellites.xml")
    archive.close()


def create_file_xml(tree, user_id):
    with open("media/satellites.xml", "wb") as fh:
        tree.write(fh)

    with open("media/satellites.xml", "r") as fin:
        data = fin.read()
    with open("media/satellites.xml", "wt") as fout:
        fout.write(beautify_xml(data))

    zpifile(user_id)


def download_provider():
    logit = list()
    provider = list()
    for continent in ("asia", "europe", "atlantic", "america"):
        try:
            url = f"https://www.lyngsat.com/packages/{continent}.html"
            response = httpx.get(url)
            soup = BeautifulSoup(response.text, "lxml")
            quotes = soup.find("table", {"class": "bigtable"})
            tbody_tag = quotes.contents
            tr_tag = tbody_tag[1]
            td_tag = tr_tag.contents[3]
            for element in td_tag.find_all("font"):
                if element.text[-2:] in ("°E", "°W") and re.findall(
                    "[0-9]", element.text
                ):
                    logit.append(element.text)

            for a_tag in td_tag.find_all("a"):
                if a_tag.text.__contains__("Freq."):
                    provider.append(f'{a_tag.get("href")[33:]}')

        except httpx.RequestError as exc:  # An error occurred while requesting
            print(
                "HTTPSRequestError!",
                f"An error occurred while requesting {exc.request.url!r}.",
            )

        except httpx.HTTPStatusError as exc:  # Error status_code 4xx,5xx
            print(
                "HTTPStatusError !",
                f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.",
            )

    return (logit, provider)


def download_sat():
    logit = list()
    satellit = list()
    for i in (
        "asia",
        "europe",
        "atlantic",
        "america",
    ):
        try:
            url = f"https://www.lyngsat.com/{i}.html"
            response = httpx.get(url)
            soup = BeautifulSoup(response.text, "lxml")
            quotes = soup.find("table", {"class": "bigtable"})
            body_tag = quotes.contents
            tr_tag = body_tag[1].contents
            td_tag = tr_tag[3].contents
            td_tr_tag = td_tag[15].contents
            # получаем название спутников
            for sat in td_tr_tag[1].find_all("a"):
                if sat.contents[0][-1] == "." and sat.get("href")[:5] != "https":
                    satellit.append(sat.get("href"))

                # получаем позицию спутника
            for lgt in td_tag[15].find_all("font"):
                if lgt.text[-2:] in ("°E", "°W") and len(lgt.text) > 2:
                    logit.append(lgt.text)

        except httpx.RequestError as exc:  # An error occurred while requesting
            print(
                "HTTPSRequestError!",
                f"An error occurred while requesting {exc.request.url!r}.",
            )

        except httpx.HTTPStatusError as exc:  # Error status_code 4xx,5xx

            print(
                "HTTPStatusError !",
                f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.",
            )

    return (logit, satellit)


def create_xml(list_box, logit, satellit, user_id):

    import xml.etree.ElementTree as xml

    root = xml.Element("satellites")  # Создаем XML файл
    root.set("version", "1.0")
    root.set("encoding", "iso-8859-1")
    named_tuple = time.localtime()
    time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
    comment = xml.Comment(text=f"source https://www.lyngsat.com/ parsing {time_string}")
    root.append(comment)
    try:
        for i in list_box:

            # Создаем sat name XML
            if logit[int(i)][-1] == "E":
                position = float(logit[int(i)][:-2]) * 10
            else:
                position = float(logit[int(i)][:-2]) * -10
            sat = xml.Element(
                "sat",
                name=f"{satellit[int(i)][:-5]} ({logit[int(i)][:-4]}{logit[int(i)][-1:]})",
                flags="0",
                position=str(position)[:-2],
            )
            root.append(sat)

            url = f"https://www.lyngsat.com/{satellit[int(i)]}"
            # try:
            response = httpx.get(url)
            soup = BeautifulSoup(response.text, "lxml")
            quotes = soup.find("table", {"class": "bigtable"})
            body_tag = quotes.contents
            tr_tag = body_tag[1].contents
            # td_tag = tr_tag[3].contents
            for i in tr_tag[3].find_all("font"):  # symbol_rate
                txt = i.text
                # print(txt)
                if (
                    re.findall("Rtp", txt)
                    or re.findall("Ltp", txt)
                    or re.findall("Htp", txt)
                    or re.findall("Vtp", txt)
                ):
                    s = txt[2:].find(" ")
                    if txt[2:].__contains__("."):
                        freq = txt[: s - 2].strip()
                    else:

                        # self.frequency.append(txt[:s].strip())
                        freq = txt[:s].strip()

                    if freq[-1] == "L":
                        polarization = "2"
                    elif freq[-1] == "R":
                        polarization = "3"
                    elif freq[-1] == "H":
                        polarization = "0"
                    elif freq[-1] == "V":
                        polarization = "1"
                if (
                    re.findall("V", txt[-1:])
                    or re.findall("H", txt[-1:])
                    or re.findall("R", txt[-1:])
                ):
                    if (
                        re.findall("\d", txt.strip()[:1])
                        and not re.findall("Htp", txt)
                        and not re.findall("Vtp", txt)
                        and not re.findall("Rtp", txt)
                    ):
                        freq = txt.strip()
                        if txt[-1] == "H":
                            polarization = "0"
                        elif txt[-1] == "V":
                            polarization = "1"
                        elif txt[-1] == "R":
                            polarization = "3"

                if re.findall("DVB", txt):
                    if txt not in ("DVB-S", "DVB-S2", "non-DVB"):
                        if re.findall("DVB-S28PSK", txt):
                            s = txt.find("DVB-S28PSK")
                            s += 10
                            s2 = txt.find("/")
                            s2 -= 1
                            # self.symbol_rate.append(txt[s + 10 : s2 - 1])
                            symbol = txt[s:s2]
                            system, modulation = "1", "2"
                            if s2 == -1:
                                s += 10
                                symbol = txt[s:]
                        elif re.findall("DVB-S2X8PSK", txt):
                            # self.symbol_rate.append(txt[11:-5])
                            symbol = txt[11:-5]
                            system, modulation = "1", "2"
                        elif re.findall("DVB-S2XACM", txt):
                            # self.symbol_rate.append(txt[10:-1])
                            symbol = txt[10:-1]
                            system, modulation = "1", "2"

                        elif re.findall("DVB-S2ACM", txt):
                            # self.symbol_rate.append(txt[9:-1])
                            s2 = txt.find("/") - 1
                            symbol = txt[9:s2]
                            if txt[-1] == ".":
                                symbol = txt[9:-1]
                            system, modulation = "1", "2"

                        elif re.findall("DVB-S216APSK", txt):
                            s = txt.find("DVB-S216APSK") + 12
                            s2 = txt.find("/") - 1
                            # self.symbol_rate.append(txt[s + 12 : s2 - 1])
                            symbol = txt[s:s2]
                            system, modulation = "1", "4"

                        elif re.findall("DVB-S2X16APSK", txt):
                            s2 = txt.find("/") - 1
                            symbol = txt[13:s2]
                            system, modulation = "1", "4"

                        elif re.findall("DVB-S232APSK", txt):
                            s2 = txt.find("/") - 1
                            symbol = txt[12:s2]
                            system, modulation = "1", "4"

                        elif re.findall("DVB-S2X32APSK", txt):
                            s2 = txt.find("/") - 1
                            symbol = txt[13:s2]
                            system, modulation = "1", "4"

                        elif re.findall("DVB-S2QPSK", txt):
                            s2 = txt.find("/")
                            y = s2 - 1
                            # self.symbol_rate.append(txt[10 : s2 - 1])
                            symbol = txt[10:y]
                            system, modulation = "1", "2"
                            if s2 == -1:
                                symbol = txt[10:]

                        elif re.findall("DVB-S8PSK", txt):
                            if txt.__contains__("Turbo"):
                                s2 = txt.find("/") - 1
                                symbol = txt[15:s2]
                                system, modulation = "0", "2"
                            else:
                                s2 = txt.find("/") - 1
                                symbol = txt[9:s2]
                                system, modulation = "0", "2"
                                if s2 == -1:
                                    symbol = txt[9:]

                        elif re.search("^DVB-S2.*[0-4]$", txt) and not re.findall(
                            "/", txt
                        ):
                            system, modulation = "1", "1"
                            symbol = txt[6:]

                        elif re.findall("DVB-S", txt):
                            if txt.__contains__("Turbo"):
                                s = txt.find("DVB-S") + 11
                                s2 = txt.find("/") - 1
                                system, modulation = "0", "1"
                                symbol = txt[s:s2]
                            else:
                                s = txt.find("DVB-S")
                                s2 = txt.find("/")
                                system, modulation = "0", "1"
                                z, y = s + 5, s2 - 1
                                if len(txt[z:y]) > 5:
                                    s += 6
                                    s2 -= 1
                                    # self.symbol_rate.append(txt[s+6:s2-1])
                                    symbol = txt[s:s2]

                                else:
                                    # self.symbol_rate.append(txt[s+5:s2-1])
                                    s += 5
                                    s2 -= 1
                                    symbol = txt[s:s2]
                                    if (
                                        s2 == -1
                                        or re.search("^DVB-S.*[0-9]$", txt)
                                        and not re.findall("/", txt)
                                    ):
                                        symbol = txt[s:]
                        if txt[-3:] == "1/2":
                            fec = "1"
                        elif txt[-3:] == "2/3":
                            fec = "2"
                        elif txt[-3:] == "3/4":
                            fec = "3"
                        elif txt[-3:] == "5/6":
                            fec = "4"
                        elif txt[-3:] == "7/8":
                            fec = "5"
                        else:
                            fec = "0"

                        xml.SubElement(
                            sat,
                            "transponder",
                            {
                                "frequency": f"{freq[:-2]}000",
                                "symbol_rate": f"{symbol}000",
                                "polarization": polarization,
                                "fec_inner": fec,
                                "system": system,
                                "modulation": modulation,
                            },
                        )

    except httpx.RequestError as exc:
        print(f"An error occurred while requesting {exc.request.url!r}.")

    except httpx.HTTPStatusError as exc:
        print(
            f"Error response {exc.response.status_code} while requesting {exc.request.url!r}."
        )

    tree = xml.ElementTree(root)
    create_file_xml(tree, user_id)


def create_provider_xml(list_box, logit, provider):

    root = xml.Element("satellites")  # Создаем XML файл
    root.set("version", "1.0")
    root.set("encoding", "iso-8859-1")
    named_tuple = time.localtime()
    time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
    comment = xml.Comment(text=f"source https://www.lyngsat.com/ parsing {time_string}")
    root.append(comment)
    try:
        for i in list_box:

            # Создаем sat name XML
            if logit[int(i)][-1] == "E":
                position = float(logit[int(i)][:-2]) * 10
            else:
                position = float(logit[int(i)][:-2]) * -10
            sat = xml.Element(
                "sat",
                name=f"{provider[int(i)][:-5]} ({logit[int(i)][:-4]}{logit[int(i)][-1:]})",
                flags="0",
                position=str(position)[:-2],
            )
            root.append(sat)
            url = f"https://www.lyngsat.com/packages/{provider[int(i)]}"
            response = httpx.get(url)
            soup = BeautifulSoup(response.text, "lxml")
            quotes = soup.find("table", {"class": "bigtable"})
            body_tag = quotes.contents
            tag_tr = body_tag[1].contents
            for i in tag_tr[3].find_all("font"):  # symbol_rate
                txt = i.text
                # print(txt)
                if (
                    re.findall("Rtp", txt)
                    or re.findall("Ltp", txt)
                    or re.findall("Htp", txt)
                    or re.findall("Vtp", txt)
                    or re.search("^[0-9].* V$", txt[1:])
                    or re.search("^[0-9].* H$", txt[1:])
                ):
                    s = txt[1:].find(" ")
                    freq = txt[: s + 1]
                    if txt.__contains__("Vtp"):
                        polar = "1"
                    if txt.__contains__("Htp"):
                        polar = "0"
                    if txt.__contains__("Rtp"):
                        polar = "3"
                    if txt.__contains__("Ltp"):
                        polar = "2"
                    if re.search("^[0-9].* V$", txt[1:]):
                        polar = "1"
                    if re.search("^[0-9].* H$", txt[1:]):
                        polar = "0"
                if re.search("^DVB-S.*/$", txt[:-1]) or re.search(
                    "^DVB-S.*FEC$", txt[:-2]
                ):
                    s = txt.find(" ")
                    SR = txt[s : txt.find("FEC")].strip()
                    if re.search("^DVB.*-S28PSK$", txt[: s - 2]):
                        system = "1"
                        modl = "2"
                    if re.search("^DVB.*-S2X8PSK$", txt[: s - 2]):
                        system = "1"
                        modl = "2"
                    if re.search("^DVB.*-S2XACM$", txt[: s - 2]):
                        system = "1"
                        modl = "2"
                    if re.search("^DVB.*-S2ACM$", txt[: s - 2]):
                        system = "1"
                        modl = "2"
                    if re.search("^DVB.*-S216APSK$", txt[: s - 2]):
                        system = "1"
                        modl = "4"
                    if re.search("^DVB.*-S2X16APSK$", txt[: s - 2]):
                        system = "1"
                        modl = "4"
                    if re.search("^DVB.*-S232APSK$", txt[: s - 2]):
                        system = "1"
                        modl = "4"
                    if re.search("^DVB.*-S2X32APSK$", txt[: s - 2]):
                        system = "1"
                        modl = "4"
                    if re.search("^DVB.*-S2QPSK$", txt[: s - 2]):
                        system = "1"
                        modl = "2"
                    if re.search("^DVB.*-S8PSK$", txt[: s - 2]):
                        system = "0"
                        modl = "2"
                    if re.search("^DVB.*-S$", txt[: s - 2]):
                        system = "0"
                        modl = "1"
                    # FEC
                    if txt[-3:] == "1/2":
                        fec = "1"
                    elif txt[-3:] == "2/3":
                        fec = "2"
                    elif txt[-3:] == "3/4":
                        fec = "3"
                    elif txt[-3:] == "5/6":
                        fec = "4"
                    elif txt[-3:] == "7/8":
                        fec = "5"
                    else:
                        fec = "0"
                    if freq and polar:
                        xml.SubElement(
                            sat,
                            "transponder",
                            {
                                "frequency": f"{freq}000",
                                "symbol_rate": f"{SR}000",
                                "polarization": polar,
                                "fec_inner": fec,
                                "system": system,
                                "modulation": modl,
                            },
                        )
                        freq, polar = False, False

    except httpx.RequestError as exc:
        print(f"An error occurred while requesting {exc.request.url!r}.")
    except httpx.HTTPStatusError as exc:
        print(
            f"Error response {exc.response.status_code} while requesting {exc.request.url!r}."
        )

    tree = xml.ElementTree(root)
    create_file_xml(tree)
