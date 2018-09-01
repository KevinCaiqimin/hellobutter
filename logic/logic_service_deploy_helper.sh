#/bin/bash
module=match_service
suffix=`date +"%Y%m%d%H%M"`
cd ~
mv $module $module.$suffix
mkdir $module
cd $module
rz
tar -xf *.tar
sh restart_${module}.sh restart
cd ..
echo "deploy $module at $suffix" >> deploy_$module.log
