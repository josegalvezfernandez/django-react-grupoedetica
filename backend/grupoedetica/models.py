from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class UpperCaseCharField(models.CharField):
    """
     Clase usada para representar un CharField con las letras siempre en
     mayúsculas
    """

    def __init__(self, *args, **kwargs):
        super(UpperCaseCharField, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname, None)
        if value:
            value = value.upper()
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super(UpperCaseCharField, self).pre_save(model_instance, add)


class TipoEstancia(models.Model):
    """
    Clase que representa un tipo de estancia (e.g. dormitorio)

     Attributes
    ----------
    nombre: nombre del tipo de estancia (Dormitorio,Salón,Baño,Aseo,Cocina,
    Terraza,Lavadero,Pasillo)
    """

    nombre = models.CharField(max_length=25)

    def __str__(self):
        return self.nombre


class Estancia(models.Model):
    """
    Clase que representa una estancia dentro de una vivienda

     Attributes
    ----------
    tipo: tipo de estancia (referencia a la tabla/clase TipoEstancia)
    superficie : superficie en metros cuadrados
    superficie_cubierta : superficie en metros cuadrados (sólo difiere de la
    superficie en estancias cuyo tipo es "terraza
    numero_ventanas: numero de ventanas dentro de la Estancia"
    """

    tipo = models.ForeignKey(TipoEstancia, on_delete=models.RESTRICT)
    superficie = models.IntegerField()
    superficie_cubierta = models.IntegerField(blank=True,null=True)
    numero_ventanas = models.IntegerField(default = 1)

    def __str__(self):
        return f"{self.tipo} ({self.superficie} m2)"


class Cliente(models.Model):
    """
       Clase que representa a un cliente

        Attributes
       ----------
       user: usuario de la clase/tabla de django-user-account
       telefono: numero prefijo sin prefijo
       dni: dni con la letra o numero de pasaporte
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="cliente")
    telefono = models.CharField(max_length=15)
    dni = models.CharField(max_length=10,unique=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.dni}"


class TipoBase(models.Model):
    """
       Clase que representa un tipo de
        distribución topologica (Estancias) de
       una vivienda

        Attributes
       ----------
       nombre: nombre identificativo para una vivienda
       metros_habitables: metros cuadrados habitables
       metros_construidos: metros cuadrados construidos
    """

    nombre = models.CharField(max_length=50)
    metros_habitables = models.IntegerField()
    metros_construidos = models.IntegerField()

    def __str__(self):
        return f"{self.nombre} ({self.metros_habitables} m2)"


class EstanciaTipoBase(models.Model):
    """
       Clase que representa la relación de pertenencia de una estancia a un
        TipoBase de Vivienda

        Attributes
       ----------
       numero: identifica univocamente para cada TipoBase
        diferentes estancias del mismo tipo (e.g. dormitorio 1, dormitorio 2)
       tipo_base: TipoBase al que pertenece la Estancia (referencia a la clase/tabla
       TipoBase)
       estancia: Estancia que pertenece el TipoBase (referencia a la clase/tabla
       TipoBase)
    """

    numero = models.IntegerField(default = 1)
    tipo_base = models.ForeignKey(TipoBase, on_delete=models.RESTRICT)
    estancia = models.ForeignKey(Estancia, on_delete=models.RESTRICT)

    class Meta:
        unique_together = (('tipo_base', 'estancia'),)


class Portal(models.Model):
    """
       Clase que representa un portal de viviendas dentro de una promoción

       Attributes
       ----------
       numero: numero del portal (clave primaria)
    """

    numero = models.IntegerField(primary_key=True)

    def __str__(self):
        return f"Portal {self.id}"


class DocumentoPortalPromocion(models.Model):
    """
       Clase que representa un documento del portal de la promoción

       Attributes

       ---------
       titulo: titulo del documento (valor único)
       ruta_documento: ruta del documento dentro del servidor
       descripcion: descripcion detallada del documento
       portal: portal vinculado al documento (referencia a la tabla/clase Portal)
       fecha_creacion: fecha creacion del documento
    """

    titulo = models.CharField(max_length=100,unique=True)
    ruta_documento = models.CharField(max_length=255,unique=True)
    descripcion = models.TextField(null = True)
    portal = models.ForeignKey(Portal,on_delete =models.RESTRICT)
    fecha_creacion= models.DateField()


class TipoBasePortal(models.Model):
    """
       Clase que representa la relacion entre un TipoBase y un Portal

       Attributes
       ---------
       portal: portal en el que encontramos el TipoBase de Vivienda
       (referencia a la tabla/clase Portal)
       tipo_base: TipoBase de Vivienda que encontramos en un Portal
       (referencia a la tabla/clase TipoBase)
       letra: letra en que encontramos un TipoBase de Vivienda en un Portal
    """

    portal = models.ForeignKey(Portal,on_delete=models.RESTRICT)
    tipo_base = models.ForeignKey(TipoBase,on_delete=models.RESTRICT)
    letra = models.CharField(max_length=1)

    def __str__(self):
        return f"{self.tipo_base} - {self.portal}"


class DocumentoTipoBasePortal(models.Model):
    """
           Clase que representa un documento de un TipoBase de Vivienda para
           un Portal

           Attributes

           ---------
           titulo: titulo del documento (valor único)
           ruta_documento: ruta del documento dentro del servidor
           descripcion: descripcion detallada del documento
           portal: portal vinculado al documento (referencia a la tabla/clase Portal)
           fecha_creacion: fecha creacion del documento
    """

    titulo = models.CharField(max_length=100,unique=True)
    ruta_documento= models.CharField(max_length=255,unique=True)
    descripcion = models.TextField()
    inmueble_tipo_portal =models.ForeignKey(TipoBasePortal,on_delete=models.RESTRICT)

class Inmueble(models.Model):
    piso = models.IntegerField()
    letra = UpperCaseCharField(max_length=3)
    id_trastero = models.IntegerField()
    superficie_trastero = models.IntegerField()
    tipo = models.ForeignKey(TipoBasePortal,on_delete=models.RESTRICT)
    propietario = models.ForeignKey(Cliente,on_delete=models.RESTRICT)
    compra_venta_firmada = models.BooleanField(default = False)


    def __str__(self):
        if self.piso == 0:
           return f"{self.tipo} - Bajo {self.letra}    {self.propietario}"
        else:
           return f"{self.tipo} - {self.piso}º {self.letra}    {self.propietario}"
    def to_str_inmuebles_propietario(self):
        if self.piso == 0:
           return f"{self.tipo} - Bajo {self.letra}"
        else:
           return f"{self.tipo} - {self.piso}º {self.letra}"


class DocumentoInmueble(models.Model):
    titulo = models.CharField(max_length=100,unique=True)
    ruta_documento = models.CharField(max_length=255, unique=True)
    descripcion = models.TextField()
    inmueble = models.ForeignKey(Inmueble,on_delete=models.RESTRICT)

class PlazaGaraje(models.Model):
    largo = models.IntegerField()
    ancho = models.IntegerField()
    inmueble = models.ForeignKey(Inmueble,on_delete=models.RESTRICT)
    portal = models.ForeignKey(Portal,on_delete=models.RESTRICT)

class TipoVotacion(models.Model):
    nombre = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre


class Votacion(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=50)
    tipo = models.ForeignKey(TipoVotacion,on_delete=models.RESTRICT)
    portal = models.ForeignKey(Portal,on_delete=models.RESTRICT)
    inmueble_tipo_portal = models.ForeignKey(InmuebleTipoPortal,on_delete=models.RESTRICT)

class OpcionVoto(models.Model):
    opcion = models.CharField(max_length=100)
    votacion = models.ForeignKey(Votacion,on_delete=models.RESTRICT)

class ClienteOpcionVoto(models.Model):
    cliente = models.ForeignKey(Cliente,on_delete=models.RESTRICT)
    opcion_voto = models.ForeignKey(OpcionVoto,on_delete=models.RESTRICT)

    class Meta:
        unique_together = (('cliente', 'opcion_voto'),)

class ConfiguracionInmueble(models.Model):
    nombre = models.CharField(max_length= 50)
    descripcion = models.TextField()
    fecha_limite = models.DateField()


class OpcionConfiguracion(models.Model):
    precio = models.FloatField(default=0)
    opcion = models.CharField(max_length= 100)
    configuracion = models.ForeignKey(ConfiguracionInmueble,on_delete=models.RESTRICT)
    predeterminada = models.BooleanField(default=False)

class OpcionConfiguracionSeleccionada(models.Model):
    ruta_documento= models.CharField(max_length=100)
    inmueble = models.ForeignKey(Inmueble,on_delete=models.RESTRICT,null=True)
    opcion_configuracion = models.ForeignKey(OpcionConfiguracion,on_delete=models.RESTRICT,null=True)

class DocumentoConfiguracionInmueble(models.Model):
    titulo = models.CharField(max_length=100, unique=True)
    ruta_documento = models.CharField(max_length=100)
    descripcion = models.TextField()
    opcion_configuracion_inmueble = models.ForeignKey(OpcionConfiguracionSeleccionada,on_delete=models.RESTRICT)

def cargar_tipo_estancia():
    tipo_estancias = ["Dormitorio","Salón","Baño","Aseo","Cocina","Terraza","Lavadero","Pasillo"]
    for estancia in tipo_estancias:
        tipo_estancia=TipoEstancia(nombre=estancia)
        tipo_estancia.save()
