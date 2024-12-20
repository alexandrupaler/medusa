SCRIPTTORUN="
export PYTHONPATH=$PYTHONPATH:/medusa
cd /medusa
python3 $@
"

apptainer exec -B $(pwd):/medusa -e -C apptainer/images/medusa.sif bash -c "$SCRIPTTORUN"
