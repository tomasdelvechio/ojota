import json
import os


PATH_DATOS_JSON = "datos_json"

def cod_datos_actual(cod_datos):
    """Setea el juego de datos actual."""
    SerializadoJson.COD_DATOS_ACTUAL = cod_datos


class SerializadoJson(object):
    """Clase con instancias listadas en un archivo json."""
    COD_DATOS_ACTUAL = ''
    nombre_plural = 'SerializadosJson' # redefinir al heredar
    json_en_raiz = True # redefinir al heredar

    def __init__(self, _pk=None, **kwargs):
        if _pk is not None:
            self.codigo = _pk
        else:
            for key, val in kwargs.iteritems():
                setattr(self, key, val)


    @classmethod
    def _leer_json(cls):
        """Lee las instancias desde json y arma un dict con la clave
           especificada en el parametro clave.
           Admite filtrar por mesa cuando los datos son de un json que esta en
           el subdirectorio de datos que una mesa usa."""
        nombre_cache = '_cache_' + cls.nombre_plural

        if not cls.json_en_raiz and SerializadoJson.COD_DATOS_ACTUAL:
            nombre_cache += '_' + SerializadoJson.COD_DATOS_ACTUAL

        if nombre_cache not in dir(cls):
            # se pluraliza el nombre de la clase para obtener el nombre del
            # archivo (ej: Persona -> Personas.json)
            if cls.json_en_raiz or not SerializadoJson.COD_DATOS_ACTUAL:
                path_json = os.path.join(PATH_DATOS_JSON,
                                         cls.nombre_plural + '.json')
            else:
                path_json = os.path.join(PATH_DATOS_JSON,
                                         SerializadoJson.COD_DATOS_ACTUAL,
                                         cls.nombre_plural + '.json')

            datos = json.load(open(path_json, 'r'))
            elementos = dict((datos_elemento['codigo'], datos_elemento)
                             for datos_elemento in datos)
            setattr(cls, nombre_cache, elementos)
        return getattr(cls, nombre_cache)

    @classmethod
    def get(cls, codigo=None, **kargs):
        """Obtiene el primer elemento que cumpla con las condiciones."""
        if codigo:
            kargs['codigo'] = codigo
        if kargs.keys() == ['codigo']:
            codigo = kargs['codigo']
            todos = cls._leer_json()
            if codigo in todos:
                return cls(**todos[codigo])
            else:
                return None
        else:
            resultado = cls.all(**kargs)
            if resultado:
                return resultado[0]
            else:
                return None

    @classmethod
    def _sort(cls, lista, campos_orden):
        campos_orden = [x.strip() for x in campos_orden.split(',')]

        for campo_orden in reversed(campos_orden):
            if campo_orden.startswith('-'):
                invertir = True
                campo_orden = campo_orden[1:]
            else:
                invertir = False

            lista = sorted(lista,
                           key=lambda e: getattr(e, campo_orden),
                           reverse=invertir)
        return lista

    @classmethod
    def all(cls, **kargs):
        """Obtiene la lista de elementos que cumplen las condiciones."""
        todos = cls._leer_json().values()
        campos_orden = None
        if 'sorted' in kargs:
            campos_orden = kargs['sorted']
            del kargs['sorted']

        lista = [cls(**datos_elemento)
                 for datos_elemento in todos
                 if all(datos_elemento[campo] == valor
                        for campo, valor in kargs.items())]

        if campos_orden:
            lista = cls._sort(lista, campos_orden)

        return lista

    def __eq__(self, other):
        return self.codigo == other.codigo

    def __repr__(self):
        return '%s<%s>' % (self.__class__.__name__.split('.')[-1], self.codigo)

class Persona(SerializadoJson):
    """Lista que agrupa personas."""
    nombre_plural = 'Personas'
