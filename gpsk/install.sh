#!/bin/bash

ruta="/home/daniel/dev/is2-env/is2/"
# Posicionandonos en el directorio raíz
cd ../
echo "----Recolectando archivos del sistema----"


# Borrar los archivos anteriores
echo -e "\nBorrando archivos antiguos"
if [ -d /var/www/is2/ ]; then
  sudo rm -r /var/www/is2/
fi


if [ "$?" -ne 0 ]
then
    echo -e "ERROR: No se pudieron borrar los archivos del directorio /var/www/is2/"
    exit 1
fi
echo -e "Archivos borrados\n"


# Copiar los archivos al directorio servido por apache2
echo "Copiando archivos"
sudo cp -r "$ruta" /var/www/
if [ "$?" -ne 0 ]
then
    echo -e "ERROR: No se pudo copiar el directorio a /var/www/"
    exit 1
fi

#Otorgar permisos correspondientes
sudo chown -R www-data:www-data /var/www/*
sudo chmod -R 777 /var/www/*
if [ "$?" -ne 0 ]
then
    echo -e "ERROR: No se pudo cambiar permisos del directorio /var/www/is2"
    exit 1
fi

#Configuracion Apache
echo -e "----Configurando Apache----"
sudo mv /var/www/is2/gpsk/gpsk.com.conf /etc/apache2/sites-available/
if [ "$?" -ne 0 ]
then
    echo -e "ERROR: No se puede mover los archivos de configuracion desde /var/www/sgpa2015/conf/ a /etc/apache2/sites-available"
    exit 1
fi

#sudo rm -r /var/www/is2/gpsk/gpsk.conf
#if [ "$?" -ne 0 ]
#then
 #   echo -e "ERROR: No se pudo borrar el directorio de configuracion"
  #  exit 1
#fi

echo -e "Activando los sitios [gpsk] en Apache"
sudo a2ensite gpsk.com.conf
if [ "$?" -ne 0 ]
then
    echo -e "ERROR: No se pudo activar el sitio"
    exit 1
fi

echo -e "Recargando Apache"

sudo service apache2 restart
if [ "$?" -ne 0 ]
then
    echo -e "ERROR: No se pudo recargar el servicio apache2"
    exit 1
fi

# Verificar si estos datos en /etc/hosts antes de agregarlos, actualmente se agregan cada vez que se ejecuta el archivo
sudo echo -e "----Fix[sin DNS]: Agrega el nombre y direccion de la pagina a los hosts conocidos de la maquina.----"
sudo sh -c "echo '127.0.0.1 gpsk.com' >> /etc/hosts"


#Otorgar permisos correspondientes versionII
sudo chown -R www-data:www-data /var/www/
sudo chmod -R 777 /var/www/
if [ "$?" -ne 0 ]
then
    echo -e "ERROR: No se pudo cambiar permisos del directorio /var/www/is2"
    exit 1
fi

#source /home/$USER/PycharmProjects/env/bin/activate
cd /var/www/is2/gpsk
python manage.py collectstatic --settings=gpsk.settings.production



echo "************** Este es un comentario ************"

#Creación de la Base de Datos

su postgres "crearBD.sql"

echo "************** Poblando la base de datos de produccion ************"
python manage.py makemigrations --settings=gpsk.settings.production
echo "makemigrate hecho"

python manage.py migrate --settings=gpsk.settings.production
echo "migrate hecho"

python manage.py loaddata --verbosity=2 3proyectos_final.json --settings=gpsk.settings.production
echo "Poblacion exitosa"

sudo service apache2 restart

firefox gpsk.com &&

clear
echo "***********Configuracion exitosa**********************"
exit 0
