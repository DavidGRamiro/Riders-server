# Configuración de Valhalla con Docker para España

**Proyecto:** Riders\
**Estado de esta documentación:** 6 de noviembre de 2026\
**Situación actual:** descarga del extracto de OpenStreetMap de España
en curso; todavía no se ha confirmado la generación de los tiles ni que
el servidor esté listo.

------------------------------------------------------------------------

## 1. Objetivo

Integrar **Valhalla** como motor de cálculo de rutas por carretera para
la aplicación Riders.

La arquitectura prevista es:

-   **Frontend:** Angular, para mostrar el mapa y la geometría de la
    ruta.
-   **Backend:** Django/Python, para solicitar el cálculo de rutas a
    Valhalla.
-   **Motor de routing:** Valhalla, ejecutándose en un contenedor
    Docker.
-   **Datos cartográficos:** extracto de OpenStreetMap de España,
    obtenido de Geofabrik.

Valhalla utiliza los datos de OpenStreetMap para construir una
representación interna de la red de carreteras. Esa representación se
almacena en tiles y se reutiliza en las peticiones de routing. No es
necesario descargar y procesar el mapa en cada petición.

## 2. Estructura del proyecto

El archivo `docker-compose.yml` está situado en la raíz del proyecto. Se
ha preparado esta estructura:

``` text
Riders/
├── docker-compose.yml
├── valhalla/
│   └── custom_files/
├── backend/
└── ...
```

La carpeta `valhalla/custom_files/` se utiliza para persistir en el
equipo los archivos que Valhalla descarga y genera.

> Importante: el nombre utilizado en la configuración es `custom_files`
> (con guion bajo), no `custom-files`.

Crear la carpeta desde la raíz del proyecto:

``` bash
mkdir -p valhalla/custom_files
```

## 3. Docker Compose

Configuración utilizada:

``` yaml
services:
  valhalla:
    image: ghcr.io/valhalla/valhalla-scripted:latest
    container_name: valhalla
    ports:
      - "8002:8002"
    volumes:
      - ./valhalla/custom_files:/custom_files
    environment:
      - tile_urls=https://download.geofabrik.de/europe/spain-latest.osm.pbf
      - use_tiles_ignore_pbf=False
      - server_threads=2
      - build_elevation=False
      - build_admins=True
      - build_time_zones=True
      - build_transit=False
      - serve_tiles=True
    restart: unless-stopped
```

### Explicación de los ajustes principales

  -----------------------------------------------------------------------------
  Configuración                             Función
  ----------------------------------------- -----------------------------------
  `image`                                   Imagen Docker de Valhalla con
                                            scripts de configuración y
                                            construcción.

  `container_name`                          Nombre asignado al contenedor:
                                            `valhalla`.

  `8002:8002`                               Expone el puerto 8002 del
                                            contenedor en el equipo anfitrión.

  `./valhalla/custom_files:/custom_files`   Comparte la carpeta local con la
                                            ruta `/custom_files` dentro del
                                            contenedor.

  `tile_urls`                               Indica el extracto de OpenStreetMap
                                            que se descargará. En este caso,
                                            España.

  `use_tiles_ignore_pbf=False`              Se establece explícitamente para
                                            que el proceso no ignore el PBF
                                            local al decidir si debe construir
                                            los tiles.

  `server_threads=2`                        Número de hilos del servidor
                                            configurado en este ejemplo.

  `build_elevation=False`                   Desactiva la construcción de datos
                                            de elevación.

  `build_admins=True`                       Habilita la construcción de datos
                                            administrativos.

  `build_time_zones=True`                   Habilita la construcción de zonas
                                            horarias.

  `build_transit=False`                     Desactiva la construcción de datos
                                            de transporte público.

  `serve_tiles=True`                        Habilita el servicio de tiles.

  `restart: unless-stopped`                 Permite que Docker reinicie el
                                            contenedor salvo que se haya
                                            detenido explícitamente.
  -----------------------------------------------------------------------------

La configuración debe validarse con la versión concreta de la imagen
utilizada. En este proyecto se ha iniciado con Valhalla
`3.9.1-8e84136b2`.

## 4. Descargar y arrancar Valhalla

Todos los comandos siguientes se ejecutan desde la raíz del proyecto,
donde está `docker-compose.yml`.

Arrancar los servicios en segundo plano:

``` bash
docker compose up -d
```

Consultar el estado:

``` bash
docker compose ps
```

Seguir los logs en directo:

``` bash
docker compose logs -f valhalla
```

Consultar las últimas 80 líneas:

``` bash
docker compose logs --tail=80 valhalla
```

## 5. Cómo funciona la descarga y construcción

La imagen `valhalla-scripted` ejecuta un proceso de preparación. En
términos generales, el flujo es:

1.  Comprueba si ya existen tiles de routing reutilizables.
2.  Si no los encuentra, descarga el PBF indicado en `tile_urls`.
3.  Procesa el PBF y construye los tiles de Valhalla.
4.  Prepara e inicia el servidor HTTP.

Los tiles son los datos internos que el motor consulta para calcular
rutas. El archivo PBF es el extracto original de OpenStreetMap; no es
todavía el grafo de routing ya construido.

La primera descarga y construcción pueden tardar bastante y consumir
recursos de CPU, memoria y disco. Conviene dejar el contenedor
funcionando hasta que termine el proceso.

### Mensajes observados durante el arranque

``` text
Valhalla version: 3.9.1-8e84136b2

find: '/custom_files/transit_tiles': No such file or directory

WARNING: No routing tiles found at /custom_files/valhalla_tiles.tar
or /custom_files/valhalla_tiles, starting a new build

WARNING: No local files and no valhalla_tiles.tar found.
Downloading links: https://download.geofabrik.de/europe/spain-latest.osm.pbf!
```

Interpretación:

-   El contenedor ha arrancado con Valhalla 3.9.1.
-   No había tiles previos, por lo que es razonable que indique que va a
    iniciar una nueva construcción.
-   El aviso de `transit_tiles` está relacionado con los datos de
    transporte público, que no se están construyendo
    (`build_transit=False`). Por sí solo no demuestra que el routing por
    carretera haya fallado.
-   La ausencia inicial de `valhalla_tiles` es esperable en una
    instalación nueva.

## 6. Redirección de Geofabrik

Al consultar la URL de descarga se recibió:

``` text
HTTP/1.1 307 Temporary Redirect
Location: https://download.geofabrik.de/europe/spain-261104.osm.pbf
```

Esto indica que la URL `spain-latest.osm.pbf` redirige al extracto
fechado. Una redirección HTTP 307 no es por sí misma un error.

En la salida inicial de los logs apareció una descarga de 267 bytes. Esa
cifra correspondía a la respuesta de redirección observada en aquella
salida, no al tamaño completo del extracto.

Después se comprobó que el contenedor estaba ejecutando:

``` text
curl --location -o /custom_files/spain-latest.osm.pbf \
https://download.geofabrik.de/europe/spain-latest.osm.pbf
```

La opción `--location` permite a `curl` seguir la redirección.

## 7. Volumen Docker: dónde aparecen los archivos

El montaje configurado es:

``` yaml
volumes:
  - ./valhalla/custom_files:/custom_files
```

Esto establece una correspondencia directa:

  Equipo local                      Dentro del contenedor
  --------------------------------- -----------------------
  `Riders/valhalla/custom_files/`   `/custom_files/`

Por tanto, los archivos escritos por Valhalla dentro de `/custom_files`
deben aparecer también en `valhalla/custom_files/` en el proyecto local.

Para listar el contenido desde el contenedor:

``` bash
docker exec -it valhalla ls -lah /custom_files
```

Para listar archivos:

``` bash
docker exec -it valhalla find /custom_files -maxdepth 2 -type f
```

Para consultar el montaje configurado:

``` bash
docker inspect valhalla
```

En la sección `Mounts` se debe comprobar que `Source` apunta a la
carpeta local esperada y que `Destination` es `/custom_files`.

## 8. Comprobar el progreso de la descarga

Consultar el tamaño del PBF:

``` bash
docker exec -it valhalla stat -c '%s bytes - %y' \
  /custom_files/spain-latest.osm.pbf
```

Ejecutar el comando varias veces, dejando pasar un intervalo, permite
comprobar si el archivo sigue creciendo.

También se puede revisar qué procesos están activos:

``` bash
docker exec -it valhalla ps aux
```

Durante la descarga se observó este proceso:

``` text
root 26 ... curl --location -o /custom_files/spain-latest.osm.pbf \
https://download.geofabrik.de/europe/spain-latest.osm.pbf
```

Esto confirmó que `curl` estaba descargando el extracto y siguiendo la
redirección.

Para observar el consumo de recursos:

``` bash
docker stats valhalla
```

Para consultar las cabeceras HTTP y seguir las redirecciones:

``` bash
docker exec -it valhalla curl -IL \
  https://download.geofabrik.de/europe/spain-latest.osm.pbf
```

La utilidad `file` no está instalada en la imagen utilizada, por lo que
este comando falló:

``` bash
docker exec -it valhalla file /custom_files/spain-latest.osm.pbf
```

Ese error solo indica que el ejecutable `file` no está disponible dentro
del contenedor; no demuestra que el PBF sea inválido.

## 9. Estado actual del proyecto

En la última comprobación compartida, el tamaño del archivo era:

``` text
363712512 bytes
```

Es decir, aproximadamente 346 MiB.

El listado de procesos mostraba:

``` text
root 1  ... bash /valhalla/scripts/docker-entrypoint.sh build_tiles
root 10 ... bash /valhalla/scripts/configure_valhalla.sh ...
root 26 ... curl --location -o /custom_files/spain-latest.osm.pbf ...
```

**Conclusión del estado actual:** la descarga del PBF estaba en curso.
Todavía no se había confirmado que hubiera terminado ni que Valhalla
hubiera comenzado a construir los tiles.

No se debe considerar el motor listo solamente porque el contenedor
figure como `running`.

### Próxima comprobación

1.  Consultar de nuevo el tamaño del PBF.
2.  Comprobar si el proceso `curl` sigue activo.
3.  Revisar los logs para detectar el paso desde la descarga a la
    construcción de tiles.
4.  Esperar a que termine la construcción y se inicie el servidor.

Comandos:

``` bash
docker exec -it valhalla stat -c '%s bytes' \
  /custom_files/spain-latest.osm.pbf

docker exec -it valhalla ps aux

docker compose logs --tail=100 valhalla
```

Cuando la construcción termine, se espera encontrar datos de routing,
normalmente bajo una ruta como `/custom_files/valhalla_tiles` o un
archivo de tiles empaquetado. La estructura exacta depende del proceso
de la imagen.

## 10. Operaciones habituales del contenedor

Parar Valhalla sin eliminar el contenedor:

``` bash
docker compose stop valhalla
```

Volver a arrancarlo:

``` bash
docker compose start valhalla
```

Reiniciarlo:

``` bash
docker compose restart valhalla
```

Detener y eliminar los contenedores de Compose:

``` bash
docker compose down
```

Volver a crear e iniciar los contenedores:

``` bash
docker compose up -d
```

Consultar el estado:

``` bash
docker compose ps
```

Los datos guardados en `./valhalla/custom_files` permanecen en el equipo
local cuando se ejecuta `docker compose down`, porque se trata de un
montaje de carpeta local. No borrar esa carpeta si se quieren conservar
los datos descargados y los tiles generados.

Durante la descarga o construcción inicial, evitar parar o recrear el
contenedor salvo que haya un error que lo requiera.

## 11. Advertencia pendiente: variable de Compose

Al ejecutar `docker compose logs` aparecieron tres avisos como este:

``` text
WARN[0000] The "yuzvudarut5" variable is not set.
Defaulting to a blank string.
```

Este aviso lo emite Docker Compose al interpretar el archivo de
configuración; no es un mensaje de Valhalla.

Compose puede interpretar una expresión `$NOMBRE` dentro del YAML como
una variable de entorno. Hay que revisar el archivo para localizar la
cadena `yuzvudarut5` y determinar si procede de una contraseña, token u
otro valor que contenga `$`.

Comprobar la configuración resuelta:

``` bash
docker compose config
```

Si un valor literal contiene `$`, puede ser necesario escaparlo como
`$$` en el archivo Compose. Antes de modificarlo, identificar
exactamente el valor y su propósito. No compartir públicamente secretos,
tokens ni contraseñas que puedan aparecer en la configuración.

## 12. Próximos pasos una vez finalice la construcción

Una vez que los tiles estén generados y el servidor esté listo:

1.  Comprobar el estado del servidor mediante su endpoint de estado, si
    está habilitado en la configuración.
2.  Probar una petición HTTP de routing contra Valhalla, normalmente en
    `http://localhost:8002/route`.
3.  Enviar desde Django las coordenadas de origen, puntos intermedios y
    destino.
4.  Utilizar el costing `motorcycle` para el cálculo de rutas de moto,
    comprobando las opciones soportadas por la versión y el grafo
    construido.
5.  Devolver al frontend la geometría de la ruta para representarla con
    Leaflet.

Si Django se ejecuta en otro contenedor de la misma red Docker, no debe
utilizar `localhost:8002` para acceder a Valhalla: debe utilizar el
nombre del servicio Docker, por ejemplo `http://valhalla:8002`, y ambos
contenedores deben compartir una red.

------------------------------------------------------------------------

## Referencias

-   Valhalla Docker: https://github.com/valhalla/valhalla-docker
-   Valhalla: https://github.com/valhalla/valhalla
-   Geofabrik -- extracto de España:
    https://download.geofabrik.de/europe/spain.html
-   Geofabrik -- PBF de España:
    https://download.geofabrik.de/europe/spain-latest.osm.pbf

**Nota:** esta documentación recoge el proceso realizado y el estado
observado hasta el 6 de noviembre de 2026. La descarga y la construcción
de tiles aún no estaban confirmadas como finalizadas en ese momento.
