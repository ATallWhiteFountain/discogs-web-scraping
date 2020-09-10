# external library suitable for API requests
import requests
# standard library's json parsers
import json


class ArtistsResource:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/70.0.3538.77 Safari/537.36"}

    def __init__(self, band_id):
        self.band_id = band_id

    def print_same_member_bands(self):
        try:
            response = requests.get("https://api.discogs.com/artists/" + self.band_id, headers=self.headers)
            if response.status_code == 200:
                print("Bands with same members as " + json.loads(response.text)["name"] + ":")

                ''' Wczytywanie danych o członkach zespołu. '''
                members = self.load_band_members(response)

                ''' Wczytywanie listy uczestinctw członków zadanego zespołu w innych zespołach '''
                appearances = self.load_related_bands(members)

                ''' Mając listę z uczestnictwami członków zespołu w innych zespołach, wybieram
                    takie wyniki, dla których zespół się powtarza. '''
                results = self.load_matching_results(appearances)

                ''' Metoda pomocnicza która drukuje dane w odpowiednim formacie. '''
                self.handle_output(results)
            else:
                print(response.status_code, response.reason)
        except ConnectionError:
            print("Server's response for returning band's information generated exception.")

    ''' Wczytuje członków zespołu do listy, zapisuje ich w obiektach typu Person
        o polach id i name, do których wpisuje id artysty i nazwisko artysty. '''
    @staticmethod
    def load_band_members(r):
        members = []
        try:
            for member in json.loads(r.text)["members"]:
                members.append(Person(member["id"], member["name"]))
            return members
        except KeyError:
            print("Operating on acquired json file concerning members generated exception.")

    ''' Dla każdego członka zespołu wysyłam zapytanie o zespoły w jakich uczestniczył.
        Wykorzystując odpowiedzi z serwera, zapisuje w liście obiekty typu Appearance,
        na które składają się nazwisko artysty, id grupy muzycznej w której występował,
        oraz nazwa tej grupy muzycznej.'''
    def load_related_bands(self, members):
        appearances = []
        response = ""
        for member in members:
            try:
                response = requests.get("https://api.discogs.com/artists/" + str(member.id),
                                        headers=self.headers)
            except ConnectionError:
                print("Server's response returning artist's memberships in other bands generated exception.")
            try:
                for group in json.loads(response.text)["groups"]:
                    if str(group["id"]) != self.band_id:
                        appearances.append(Appearance(member.name, group["id"], group["name"]))
            except KeyError:
                print("Operating on acquired json file concerning artists' band memberships"
                      " generated exception.")
        return appearances

    ''' Wybieram wyniki z listy wystąpień muzyków w zespołach, dla których znajdujemy, że dany zespół
        występuje więcej niż jeden raz, a więc wiemy że dla więcej niż jednego muzyka mamy zapis o byciu
        członkiem danego zespołu. 
        Zwracam do listy wynikowej results[] obiekty typu Result, zawierające pola group_name i artist_name.'''
    @staticmethod
    def load_matching_results(appearances):
        results = []
        for i in range(0, len(appearances)):
            for j in range(0, len(appearances)):
                if appearances[j].group_id == appearances[i].group_id and i != j:
                    results.append(Result(appearances[i].group_name, appearances[i].artist_name))
        return results

    ''' Dane z tablicy są sortowane. Następnie, drukuje się wyniki, nie pozwalając przy tym by ewentualne
        powtarzające się wartości były drukowane ponownie. '''
    @staticmethod
    def handle_output(tab):
        tab.sort(key=lambda element: element.group_name)
        prev_group_name = ""
        prev_artist_name = ""
        for i in range(0, len(tab)):
            if prev_group_name != tab[i].group_name and prev_artist_name != tab[i].artist_name:
                print(tab[i].group_name)
                print("-" + tab[i].artist_name)
            elif prev_artist_name != tab[i].artist_name:
                print("-" + tab[i].artist_name)
            prev_group_name = tab[i].group_name
            prev_artist_name = tab[i].artist_name


class Result:
    def __init__(self, group_name, artist_name):
        self.group_name = group_name
        self.artist_name = artist_name


class Person:

    def __init__(self, artist_id, artist_name):
        self.id = artist_id
        self.name = artist_name


class Appearance:

    def __init__(self, artist_name, group_id, group_name):
        self.artist_name = artist_name
        self.group_id = group_id
        self.group_name = group_name.split("(")[0]


if __name__ == "__main__":
    # Budka Suflera band
    question = ArtistsResource("359282")
    question.print_same_member_bands()
    # Soulfly band
    # question = ArtistsResource("40032")
    # question.print_same_member_bands()
