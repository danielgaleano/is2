#!/bin/bash
bd="gpsk-prod"
usuario="user-prod"

echo "*****************Borrando Base de Datos Existente*****************"
#su postgres -c "dropdb -w $bd -U postgres"

#su postgres 

dropdb gpsk-prod
#dropuser user-prod


echo "*****************Creando Usuario user-prod*****************"
echo "***********Ingrese el password del usuario postgres***********"
#su postgres -c 'createuser -d -a $usuario'
createuser -d -a user-prod

echo "*****************Creando Base de datos gpsk-prod*****************"
echo "***********Ingrese el password del usuario postgres***********"
#su postgres -c 'createdb $bd -O $usuario'
createdb gpsk-prod -O user-prod

echo "***********Ingrese el password del usuario postgres***********"
#su postgres -c 'psql -d $bd -a -f pass.sql -U postgres'
psql -d "$bd" -a -f pass.sql -U postgres
echo "Base de datos creada"

exit 0
