import requests, re, csv
from bs4 import BeautifulSoup
import logging
import py3langid as langid
from textblob import TextBlob

logging.basicConfig(filename='errores.log', level=logging.ERROR)

def extraer_texto_web(url):
    try:
        # Realizar la solicitud HTTP para obtener el contenido de la página web
        respuesta = requests.get(url)

        # Comprobar si la solicitud fue exitosa
        if respuesta.status_code == 200:
            # Analizar el contenido HTML de la página web
            soup = BeautifulSoup(respuesta.content, 'html.parser')

            # Extraer y limpiar el texto del contenido HTML
            texto_limpio = ' '.join(t.strip() for t in soup.stripped_strings)
            titulo = soup.title

            return texto_limpio, titulo.text
        else:
            mensaje_error = f"Error al acceder a la URL {url}: {respuesta.status_code}"
            logging.error(mensaje_error)
            return None
    except Exception as e:
        mensaje_error = f"Error al procesar la URL {url}: {e}"
        logging.error(mensaje_error)
        return None

def extraer_numeros_telefono(texto):
    try:
        # Expresión regular para extraer números de teléfono
        # Asume que los números de teléfono tienen un código de país, opcionalmente seguido de un guion, y luego un número local
        regex = re.compile(r'\+?\d{1,3}[-\s\.]?\d{8,14}')
        
        # Busca todos los números de teléfono que coincidan con la expresión regular en el texto
        numeros_encontrados = regex.findall(texto)
        
        # Retorna directamente la lista de números de teléfono encontrados
        return numeros_encontrados
    except Exception as e:
        mensaje_error = f"Error al extraer números de teléfono del texto: {e}"
        logging.error(mensaje_error)
        return None

def extraer_emails(texto, url):
    try:
        # Expresión regular para extraer correos electrónicos
        regex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        
        # Busca todos los correos electrónicos que coincidan con la expresión regular en el texto
        emails_encontrados = regex.findall(texto)
        
        return emails_encontrados
    except Exception as e:
        mensaje_error = f"Error extraer emails en {url}"
        logging.error(mensaje_error)
        return None

def detectar_idioma(texto, url):
    try:
        idioma, probabilidad = langid.classify(texto)
        return idioma
    except Exception as e:
        mensaje_error = f"Error al obtener idioma en {url}"
        logging.error(mensaje_error)
        return None

def obtener_fecha_publicacion(texto, url):
    try:
        soup = BeautifulSoup(texto, "html.parser")

        # Buscar etiquetas de tiempo
        time_tags = soup.find_all("time")
        for time_tag in time_tags:
            if "datetime" in time_tag.attrs:
                fecha_publicacion = time_tag["datetime"]
                return fecha_publicacion

        # Buscar etiquetas meta
        meta_tags = soup.find_all("meta")
        for meta_tag in meta_tags:
            if "name" in meta_tag.attrs and meta_tag["name"].lower() == "pubdate":
                if "content" in meta_tag.attrs:
                    fecha_publicacion = meta_tag["content"]
                    return fecha_publicacion

    except Exception as e:
        mensaje_error = f"Error al obtener fecha en {url}"
        logging.error(mensaje_error)
        return None

def analizar_sentimiento(texto, url):
    try:
        analysis = TextBlob(texto)
        sentiment_score = analysis.sentiment.polarity
        
        if sentiment_score > 0:
            return "positivo"
        elif sentiment_score == 0:
            return "neutro"
        else:
            return "negativo"
        
    except Exception as e:
        mensaje_error = f"Error analisis de sentimiento en {url}"
        logging.error(mensaje_error)
        return None


def extraer_dominio(url):
    dominio = url.split(".")
    dominio = dominio[1]
    return dominio


###########################################################################
#   FUNCIÓN PRINCIPAL


def main():
    
    targets_file = open("news.txt", "r")
    
    with open("resultados.csv", mode="w", newline="", encoding="utf-8") as resultados_file:
        csv_writer = csv.writer(resultados_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(["ID", "Fecha", "Dominio", "Título", "URL", "Idioma", "Sentimiento", "Telefonos", "Emails"])
        
        id_counter = 1
        for data in targets_file.readlines():
            data = data.split(",")
            url = data[1]
            date = data[0]
            try:
                texto, titulo = extraer_texto_web(url)
                dominio = extraer_dominio(url)
                resultado_tel = extraer_numeros_telefono(texto)
                resultado_email = extraer_emails(texto, url)
                idioma = detectar_idioma(texto, url)
                if date == "None":
                    #fechas = obtener_fecha_publicacion(texto, url)
                    pass
                else:
                    fechas = date

                sentimiento = analizar_sentimiento(texto, url)
                print(f"Fecha: {fechas} | Dominio: {dominio} | Título: {titulo.strip()} | URL: {url} | Idioma: {idioma} | Sentimiento: {sentimiento} | Telefonos: {resultado_tel} | Emails: {resultado_email}")
                
                csv_writer.writerow([id_counter, fechas, dominio, titulo.strip(), url.strip(), idioma, sentimiento, resultado_tel, resultado_email])
                id_counter += 1

            except Exception as e:
                print(f"{id_counter} - {e}")
                pass

main()
