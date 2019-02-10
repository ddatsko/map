import os
import folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

geolocator = Nominatim(user_agent="kumquat", timeout=3)
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=0.1)


def input_data(file, years):
    """
    (str, list) -> tuple(int, str)
    :param file: name of the file with input data
    :yield: year and location of film
    Generator of locations of shot films in given years
    """
    with open(file, 'r', errors="ignore") as f:
        for line in f:
            try:
                line = line.strip().split("\t")
                if line[-1].strip()[-1] != ')':
                    location = line[-1].strip()
                else:
                    location = line[-2].strip()
                name = line[0].strip()
                if name and name[-1] == '}':
                    name = name.split(' {')[0]
                year = int(name[-5:-1])
            except:
                continue
            if year in years:
                yield year, location


def print_progress_bar(x):
    """
    (int) -> None
    :param x: current_length of progress(of 210)
    Prints a ptogress bar
    """
    os.system("clear")
    print("[" + "|" * int(x / 2.1) + " " * int((210 - x) // 2.1) + "]")
    print("Progress: ", int(x / 2.1), "%", sep="")


def popular_countries(file):
    """
    (str) -> list(str, int)
    :param file: name of a file with data
    :return: sorted list of the most popular countries for shooted films
    """
    with open(file, 'r', errors="ignore") as f:
        countries = {}
        for line in f:
            try:
                line = line.strip()
                if line[-1] == ')':
                    line = line.split('(')[-2]
                country = line.split("\t")[-1].split()[-1]
                if country in countries:
                    countries[country] += 1
                else:
                    countries[country] = 1
            except:
                continue
        countries = list(countries.items())
        countries.sort(key=lambda x: x[1], reverse=True)
        return countries


def determine_location(name):
    """
    (str) -> list(float, float)
    :param name: the name of location
    :return: coordinates of location if it exists, else None
    """
    location = geocode(name)
    if location:
        return (location.latitude, location.longitude)
    return None


def good_year(year):
    """
    (int) -> bool
    :param year: year
    :return: whrther the year is suitable
    """
    if 1800 < year < 2020:
        return True
    return False


def get_user_data():
    """
    (None) -> list
    :return: the list of years chosen by user
    """
    os.system("clear")
    print("Enter the year(s) you`d like to discover\n\
You can type in 'YYYY' or 'YYYY-YYYY format\n\
Go on entering years untill you press 'Return'")
    res = []
    years = "1"
    while years:
        years = input("Years: ").split('-')
        if not years[0]:
            break
        try:
            if len(years) == 2:
                for i in range(int(years[0]), int(years[1]) + 1):
                    if good_year(i):
                        res.append(i)
                    elif i > 2019:
                        break
            else:
                if good_year(int(years[0])):
                    res.append(int(years[0]))
        except:
            print("Wrong input data")
    return list(set(res))


def find_popular_locations(file, years):
    """
    (str, list) -> list
    :param file: name of a file with data
    :param years: years of shot films to be considered
    :return: the most popular locations in given years
    """
    locations = {}
    for year, location in input_data(file, years):
        if location in locations:
            locations[location] += 1
        else:
            locations[location] = 1
    return sorted(locations.items(), key=lambda x: x[1], reverse=True)


def popular_locations_layer(locations, number):
    """
    (list(tuple)) -> folium.FeatureGroup()
    :param locations: sorted list of popular locations
    :param number: number of markers
    :return: folium.FeatureGroup object with placed markers
    """
    counter = 60
    fg = folium.FeatureGroup(name="Most popular locations")
    for i in range(min(number, len(locations))):
        location = determine_location(locations[i][0])
        if location:
            popup = str(locations[i][0]) + "\n" + str(locations[i][1]) + " films"
            fg.add_child(folium.Marker(location=location, icon=folium.Icon(), \
                                       popup=popup))
        counter += 1
        print_progress_bar(counter)
    return fg


def popular_countries_layer(countries, number):
    """
    list(str, int) -> folium.FeatureGroup()
    :param countries: sorted list of the most popular countries
    :param number: number of markers
    :return: folium.FeatureGroup object with placed markers
    """
    fg = folium.FeatureGroup(name="Most Popular Countries")
    counter = 0
    for country, films in countries:
        location = determine_location(country)
        if location:
            if country == "USA" or country == "UK":
                films *= 5
            else:
                films *= 10
            fg.add_child(folium.Circle(location=location, radius=films, popup=country))
        counter += 1
        print_progress_bar(counter)
        if counter >= number:
            break
    return fg


def main():
    """
    The main function of the program
    """
    films_map = folium.Map(location=[0, 0], zoom_start=2)
    years = get_user_data()
    countries = popular_countries("../docs/locations.list")
    films_map.add_child(popular_countries_layer(countries, 60))
    locations = find_popular_locations("../docs/locations.list", years)
    films_map.add_child(popular_locations_layer(locations, 150))
    films_map.add_child(folium.LayerControl())
    films_map.save("Map.html")


if __name__ == "__main__":
    main()
