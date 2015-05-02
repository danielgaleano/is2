#! /bin/bash
echo "***********Copiando el contenido de la base de datos de produccion***********"
echo "***********Ingrese el password del usuario user-prod***********"
pg_dump -c gpsk-prod -f /home/$USER/dumps/poblacion_prueba.sql -U user-prod -h localhost
echo "*************Eliminando la base de datos de produccion**************"
#dropdb gpsk-prod

echo "*****************Creando Usuario user-prod*****************"
echo "***********Ingrese el password del usuario postgres***********"
su postgres -c 'createuser -d -a user-prueba -U postgres'
echo "*****************Creando Base de datos gpsk-prod*****************"
echo "***********Ingrese el password del usuario postgres***********"
su postgres -c 'createdb gpsk-prueba -O user-prueba -U postgres'
echo "***********Ingrese el password del usuario postgres***********"
su postgres -c 'psql -d gpsk-prueba -a -f pass.sql -U postgres'

echo "*****************Poblando la base de datos de produccion*****************"
echo "***********Ingrese el password del usuario postgres***********"
su postgres -c "psql -q gpsk-prueba < poblacion_prueba.sql"

echo "*****************Copiando el proyecto a produccion*****************"
sudo cp -R /home/$USER/dev/is2-env /home/$USER/production2/
echo "*****************Activando el entorno virtual*****************"
source /home/production2/is2-env/env/bin/activate

echo "*****************Reiniciando apache*****************"
sudo /etc/init.d/apache2 restart
