#! /bin/bash
echo "***********Test***********"
echo "*****************Activando el entorno virtual*****************"
source /home/$USER/production/is2-env/env/bin/activate

#python /home/daniel/production2/is2-env/is2/gpsk/manage.py test --settings=gpsk.settings.local
cd /home/$USER/production/is2-env/is2/gpsk/
python manage.py test --settings=gpsk.settings.local
