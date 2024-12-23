from django.shortcuts import render
import requests
import os

apiKeyWeather = 1 #os.environ["forecast-api-key"]
apiKeyCoord = 1 #os.environ["coord-api-key"]

def index(request):
    return render(request, 'index.html')

def weather():
    url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&appid={apiKeyWeather}"
    response = requests.request("GET", url)
    print(response.text)

    data = response.json()
    current = data['current']
    current_weather = {
        'temperature': current['temp'],
        'feels_like': current['feels_like'],
        'humidity': current['humidity'],
        'wind_speed': current['wind_speed'],
        'description': current['weather'][0]['description']
    }

    return current_weather

def city(request):
    if request.method == 'POST':
        name = request.POST.get('city', '').strip()  # Remove whitespace
    else:
        name = ''

    # Validação do nome da cidade
    if not name:
        return {
            'error': 'Por favor, insira o nome de uma cidade.',
            'found': False
        }

    api_url = f'https://api.api-ninjas.com/v1/city?name={name}'
    
    try:
        response = requests.get(api_url, headers={'X-Api-Key': apiKeyCoord})
        
        # Verifica se a solicitação foi bem-sucedida
        if response.status_code == requests.codes.ok:
            city_data = response.json()
            
            # Verifica se algum dado de cidade foi retornado
            if city_data:
                city_info = city_data[0]  # Primeiro resultado
                return {
                    'name': city_info['name'],
                    'latitude': city_info['latitude'],
                    'longitude': city_info['longitude'],
                    'country': city_info['country'],
                    'found': True
                }
            else:
                return {
                    'error': f'Cidade "{name}" não encontrada. Por favor, verifique o nome e tente novamente.',
                    'found': False
                }
        else:
            return {
                'error': f'Erro na busca de coordenadas. Código de status: {response.status_code}',
                'found': False
            }
    
    except requests.RequestException as e:
        return {
            'error': f'Erro de conexão: {str(e)}. Tente novamente mais tarde.',
            'found': False
        }

def index(request):
    city_info = None
    weather_data = None
    
    if request.method == 'POST':
        # Coordenadas da Cidade
        city_info = city(request)
        
        # Verifica se a cidade foi encontrada
        if not city_info.get('found', False):
            # Passa o erro para o template
            return render(request, 'index.html', {
                'city_error': city_info.get('error', 'Erro desconhecido')
            })
        
        # Se as coordenadas forem encontradas, obter o clima
        try:
            # API para Clima Atual
            weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={city_info['latitude']}&lon={city_info['longitude']}&appid={apiKeyWeather}&units=metric"
            weather_response = requests.get(weather_url)
            
            # Verifica se a resposta foi bem-sucedida
            if weather_response.status_code != 200:
                raise Exception(f"Erro na API: {weather_response.status_code}")
            
            weather_json = weather_response.json()
            
            # Extrai dados completos do clima
            original_description = weather_json['weather'][0]['description'].lower()
            translated_description = WEATHER_TRANSLATIONS.get(
                original_description.capitalize(), 
                original_description.capitalize()
            )
            
            # Dados do Clima
            weather_data = {
                'city': weather_json['name'],
                'temperature': round(weather_json['main']['temp'], 1),
                'feels_like': round(weather_json['main']['feels_like'], 1),
                'humidity': weather_json['main']['humidity'],
                'pressure': weather_json['main']['pressure'],
                'wind_speed': round(weather_json['wind']['speed'], 1),
                'description': translated_description
            }
            
            # Tradução da Direção do Vento
            WIND_DIRECTIONS = {
                'N': 'Norte',
                'NE': 'Nordeste',
                'E': 'Leste',
                'SE': 'Sudeste',
                'S': 'Sul',
                'SW': 'Sudoeste',
                'W': 'Oeste',
                'NW': 'Noroeste'
            }
            
            # Direção do Vento
            if 'deg' in weather_json['wind']:
                wind_deg = weather_json['wind']['deg']
                if 337.5 <= wind_deg or wind_deg < 22.5:
                    wind_dir = 'N'
                elif 22.5 <= wind_deg < 67.5:
                    wind_dir = 'NE'
                elif 67.5 <= wind_deg < 112.5:
                    wind_dir = 'E'
                elif 112.5 <= wind_deg < 157.5:
                    wind_dir = 'SE'
                elif 157.5 <= wind_deg < 202.5:
                    wind_dir = 'S'
                elif 202.5 <= wind_deg < 247.5:
                    wind_dir = 'SW'
                elif 247.5 <= wind_deg < 292.5:
                    wind_dir = 'W'
                else:
                    wind_dir = 'NW'
                
                weather_data['wind_direction'] = WIND_DIRECTIONS.get(wind_dir, wind_dir)
        
        except Exception as e:
            weather_data = {
                'error': f'Erro ao buscar dados meteorológicos: {str(e)}'
            }
    
    return render(request, 'index.html', {
        'city_info': city_info, 
        'weather_data': weather_data
    })

def index(request):
    # Traduções de descrições do Clima
    WEATHER_TRANSLATIONS = {
        'Clear': 'Céu Limpo',
        'Clouds': 'Nublado',
        'Broken clouds': 'Nuvens Parcialmente Nubladas',
        'Scattered clouds': 'Nuvens Dispersas',
        'Few clouds': 'Poucas Nuvens',
        'Overcast clouds': 'Céu Encoberto',
        'Rain': 'Chuva',
        'Light rain': 'Chuva Leve',
        'Moderate rain': 'Chuva Moderada',
        'Heavy rain': 'Chuva Forte',
        'Freezing rain': 'Chuva Congelante',
        'Drizzle': 'Garoa',
        'Light intensity drizzle': 'Garoa Fraca',
        'Heavy intensity drizzle': 'Garoa Forte',
        'Thunderstorm': 'Tempestade',
        'Thunderstorm with light rain': 'Tempestade com Chuva Leve',
        'Thunderstorm with rain': 'Tempestade com Chuva',
        'Thunderstorm with heavy rain': 'Tempestade com Chuva Forte',
        'Snow': 'Neve',
        'Light snow': 'Neve Leve',
        'Heavy snow': 'Neve Forte',
        'Mist': 'Neblina',
        'Smoke': 'Fumaça',
        'Haze': 'Névoa',
        'Dust': 'Poeira',
        'Fog': 'Nevoeiro',
        'Sand': 'Areia',
        'Ash': 'Cinzas',
        'Squalls': 'Rajadas de Vento',
        'Tornado': 'Tornado'
    }

    city_info = None
    weather_data = None
    
    if request.method == 'POST':
        # Coordenadas da Cidade
        city_info = city(request)
        
        # Se as coordenadas forem encontradas, obter o clima
        if city_info and 'latitude' in city_info:
            try:
                # API para Clima Atual
                weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={city_info['latitude']}&lon={city_info['longitude']}&appid={apiKeyWeather}&units=metric"
                weather_response = requests.get(weather_url)
                
                # Verifica se a resposta foi bem-sucedida
                if weather_response.status_code != 200:
                    raise Exception(f"Erro na API: {weather_response.status_code}")
                
                weather_json = weather_response.json()
                
                # Extrai dados completos do clima
                original_description = weather_json['weather'][0]['description'].lower()
                translated_description = WEATHER_TRANSLATIONS.get(
                    original_description.capitalize(), 
                    original_description.capitalize()
                )
                
                # Dados do Clima
                weather_data = {
                    'city': weather_json['name'],
                    'temperature': round(weather_json['main']['temp'], 1),
                    'feels_like': round(weather_json['main']['feels_like'], 1),
                    'humidity': weather_json['main']['humidity'],
                    'pressure': weather_json['main']['pressure'],
                    'wind_speed': round(weather_json['wind']['speed'], 1),
                    'description': translated_description
                }
                
                # Tradução da Direção do Vento
                WIND_DIRECTIONS = {
                    'N': 'Norte',
                    'NE': 'Nordeste',
                    'E': 'Leste',
                    'SE': 'Sudeste',
                    'S': 'Sul',
                    'SW': 'Sudoeste',
                    'W': 'Oeste',
                    'NW': 'Noroeste'
                }
                
                # Direção do Vento
                if 'deg' in weather_json['wind']:
                    wind_deg = weather_json['wind']['deg']
                    if 337.5 <= wind_deg or wind_deg < 22.5:
                        wind_dir = 'N'
                    elif 22.5 <= wind_deg < 67.5:
                        wind_dir = 'NE'
                    elif 67.5 <= wind_deg < 112.5:
                        wind_dir = 'E'
                    elif 112.5 <= wind_deg < 157.5:
                        wind_dir = 'SE'
                    elif 157.5 <= wind_deg < 202.5:
                        wind_dir = 'S'
                    elif 202.5 <= wind_deg < 247.5:
                        wind_dir = 'SW'
                    elif 247.5 <= wind_deg < 292.5:
                        wind_dir = 'W'
                    else:
                        wind_dir = 'NW'
                    
                    weather_data['wind_direction'] = WIND_DIRECTIONS.get(wind_dir, wind_dir)
            
            except Exception as e:
                weather_data = {
                    'city': city_info['name'],
                    'error': f'Erro ao buscar dados meteorológicos: {str(e)}'
                }
    
    return render(request, 'index.html', {
        'city_info': city_info, 
        'weather_data': weather_data
    })